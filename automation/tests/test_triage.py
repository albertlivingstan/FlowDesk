import json

import httpx
import pytest
from pydantic import SecretStr

from automation.triage import SYSTEM_PROMPT, clean_text


def llm_output(**updates):
    return {"is_ticket": True, "category": "Access", "priority": "High", "summary": "Login problem",
            "description": "Cannot log in.", "confidence": 0.9, **updates}


def use_llm(settings, external, output):
    settings.llm_api_key = SecretStr("test-llm-token")
    def responder(request):
        if request.url.path.endswith("/chat/completions"):
            return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(output)}}]})
        return external.default_response(request)
    external.responder = responder


def test_llm_uses_exact_prompt_and_configured_model(client, settings, external, access_email):
    settings.llm_model = "configured-model"
    settings.llm_base_url = "https://llm.example.com/v1"
    use_llm(settings, external, llm_output())
    assert client.post("/process-email", json=access_email).json()["status"] == "created"
    body = json.loads(external.requests[0].content)
    assert body["messages"][0]["content"] == SYSTEM_PROMPT
    assert body["model"] == "configured-model"
    assert body["response_format"] == {"type": "json_object"}


@pytest.mark.parametrize("updates", [
    {"confidence": 1.1}, {"is_ticket": "true"}, {"summary": "a" * 81},
    {"category": "Other"}, {"extra_field": "not allowed"}, {"description": " "},
])
def test_invalid_llm_json_uses_rules(client, settings, external, access_email, updates):
    use_llm(settings, external, llm_output(**updates))
    result = client.post("/process-email", json=access_email).json()
    assert result["status"] == "created"
    assert result["triage"]["confidence"] == 0.93


@pytest.mark.parametrize("confidence,status", [(0.69, "needs_review"), (0.7, "created")])
def test_confidence_threshold(client, settings, external, access_email, confidence, status):
    use_llm(settings, external, llm_output(confidence=confidence))
    assert client.post("/process-email", json=access_email).json()["status"] == status
    jira_requests = [r for r in external.requests if r.url.host == "maker200222.atlassian.net"]
    assert bool(jira_requests) is (status == "created")


def test_llm_failure_uses_keyword_fallback(client, settings, external, access_email):
    settings.llm_api_key = SecretStr("test-llm-token")
    def responder(request):
        if request.url.path.endswith("/chat/completions"):
            return httpx.Response(503, json={})
        return external.default_response(request)
    external.responder = responder
    assert client.post("/process-email", json=access_email).json()["triage"]["category"] == "Access"


def test_llm_cannot_promote_newsletters(client, settings, external, access_email):
    use_llm(settings, external, llm_output())
    access_email["emailBody"] = "Newsletter: unsubscribe here"
    result = client.post("/process-email", json=access_email).json()
    assert result["status"] == "ignored"
    assert len(external.requests) == 1


def test_unsupported_critical_goes_to_review(client, settings, external, access_email):
    use_llm(settings, external, llm_output(priority="Critical"))
    assert client.post("/process-email", json=access_email).json()["status"] == "needs_review"


def test_html_cleanup():
    assert clean_text("<p>I can't log in</p><script>secret()</script><div>Please help &amp; reply</div>") == "I can't log in\nPlease help & reply"
