import base64
import json
import smtplib

import httpx
import pytest

from automation.config import Settings
from automation.models import EmailRequest
from automation.triage import SYSTEM_PROMPT, rule_based_triage


@pytest.mark.parametrize("body", [
    "Spam: claim your prize and get free money",
    "Weekly newsletter: product updates", "Buy now! Limited time offer. Unsubscribe here.",
    "Automatic reply: I am out of office until Monday",
])
def test_spam_is_ignored(client, external, body):
    result = client.post("/process-email", json={"emailSubject": "Updates", "emailBody": body,
                                               "senderEmail": "news@example.com"})
    assert result.status_code == 200
    assert result.json()["status"] == "ignored"
    assert result.json()["isTicket"] is False
    assert result.json()["ticketKey"] == ""
    assert not external.requests


def test_access_high_creates_task_with_adf_and_basic_auth(client, external, access_email):
    response = client.post("/process-email", json=access_email)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "created"
    assert result["triage"]["category"] == "Access"
    assert result["triage"]["priority"] == "High"
    assert result["ticketKey"] == "KAN-42"
    assert result["ticketUrl"] == "https://maker200222.atlassian.net/browse/KAN-42"
    assert result["confirmation"] == "logged"
    request = external.requests[-1]
    fields = json.loads(request.content)["fields"]
    assert fields["project"] == {"key": "KAN"}
    assert fields["issuetype"] == {"name": "Task"}
    assert fields["labels"] == ["Access"]
    assert fields["priority"]["name"] == "High"
    assert fields["description"]["type"] == "doc"
    assert "Reported by: customer@example.com" in json.dumps(fields["description"])
    encoded = base64.b64encode(b"automation@example.com:test-jira-token").decode()
    assert request.headers["Authorization"] == f"Basic {encoded}"
    search = json.loads(external.requests[0].content)
    assert "created >= -24h" in search["jql"]
    assert "KAN-1" in search["jql"]


def test_feature_request_low(client, external):
    result = client.post("/process-email", json={"emailSubject": "Feature request",
        "emailBody": "Please add dark mode", "senderEmail": "user@example.com"}).json()
    assert result["status"] == "created"
    assert result["triage"]["category"] == "Feature Request"
    assert result["triage"]["priority"] == "Low"
    fields = json.loads(external.requests[-1].content)["fields"]
    assert fields["labels"] == ["Feature-Request"]
    assert fields["priority"]["name"] == "Low"


def test_vague_needs_review_and_never_calls_jira(client, external):
    result = client.post("/process-email", json={"emailSubject": "Help",
        "emailBody": "Something seems odd. Can you help?", "senderEmail": "user@example.com"}).json()
    assert result["status"] == "needs_review"
    assert result["isTicket"] is True
    assert result["triage"]["confidence"] < 0.7
    assert not external.requests


def test_dry_run_is_completely_offline(client, settings, external, access_email, monkeypatch):
    from pydantic import SecretStr
    settings.dry_run = True
    settings.llm_api_key = SecretStr("unused-key")
    settings.smtp_host = "smtp.example.com"
    def forbid_smtp(*args, **kwargs):
        raise AssertionError("Dry run must not use SMTP")
    monkeypatch.setattr(smtplib, "SMTP", forbid_smtp)
    result = client.post("/process-email", json=access_email).json()
    assert result["status"] == "created"
    assert result["ticketKey"].startswith("DRY-")
    assert result["ticketUrl"] == ""
    assert result["dryRun"] is True
    assert result["confirmation"] == "logged"
    assert not external.requests


@pytest.mark.parametrize("status_code", [400, 401, 403, 429, 500, 503])
def test_jira_failure_returns_failed_without_crash(client, external, access_email, status_code, monkeypatch):
    monkeypatch.setattr("automation.jira.time.sleep", lambda _: None)
    def responder(request):
        if request.url.path.endswith("/search/jql"):
            return external.default_response(request)
        return httpx.Response(status_code, json={"errorMessages": ["sensitive upstream text"]})
    external.responder = responder
    response = client.post("/process-email", json=access_email)
    assert response.status_code == 502
    result = response.json()
    assert result["status"] == "failed"
    assert result["error"]["code"].startswith("jira_")
    assert result["confirmation"] == "not_requested"
    assert "sensitive upstream text" not in response.text
    assert result["ticketKey"] == ""


def test_duplicate_is_commented_and_not_created(client, external, access_email):
    def responder(request):
        if request.url.path.endswith("/search/jql"):
            return httpx.Response(200, json={"issues": [{"key": "KAN-40", "fields": {"summary": "  LOGIN   problem "}}]})
        return external.default_response(request)
    external.responder = responder
    result = client.post("/process-email", json=access_email).json()
    assert result["status"] == "created"
    assert result["duplicate"] is True
    assert result["ticketKey"] == "KAN-40"
    assert [request.url.path for request in external.requests] == [
        "/rest/api/3/search/jql", "/rest/api/3/issue/KAN-40/comment"]
    comment = json.loads(external.requests[-1].content)
    assert comment["body"]["type"] == "doc"
    assert "Reported by: customer@example.com" in json.dumps(comment)


def test_protected_issues_are_never_touched(client, external, access_email):
    def responder(request):
        if request.url.path.endswith("/search/jql"):
            return httpx.Response(200, json={"issues": [
                {"key": key, "fields": {"summary": "Login problem"}}
                for key in ["KAN-1", "KAN-2", "KAN-3"]]})
        return external.default_response(request)
    external.responder = responder
    result = client.post("/process-email", json=access_email).json()
    assert result["ticketKey"] == "KAN-42"
    assert not result["duplicate"]
    assert all(not request.url.path.endswith("/comment") for request in external.requests)


def test_search_uses_exact_comparison_and_pagination(client, external, access_email):
    def responder(request):
        if request.url.path.endswith("/search/jql"):
            body = json.loads(request.content)
            if body.get("nextPageToken") == "page2":
                return httpx.Response(200, json={"issues": [{"key": "KAN-41", "fields": {"summary": "Login problem"}}]})
            return httpx.Response(200, json={"issues": [{"key": "KAN-40", "fields": {"summary": "Different login problem"}}],
                                            "nextPageToken": "page2"})
        return external.default_response(request)
    external.responder = responder
    result = client.post("/process-email", json=access_email).json()
    assert result["ticketKey"] == "KAN-41"
    assert len(external.requests) == 3


def test_429_and_5xx_retry_with_retry_after(client, external, access_email, monkeypatch):
    sleeps, failures = [], [429, 503]
    monkeypatch.setattr("automation.jira.time.sleep", sleeps.append)
    def responder(request):
        if failures:
            return httpx.Response(failures.pop(0), headers={"Retry-After": "2"}, json={})
        return external.default_response(request)
    external.responder = responder
    assert client.post("/process-email", json=access_email).json()["status"] == "created"
    assert sleeps == [2, 2]


def test_jira_transport_failure_is_not_blindly_replayed(client, external, access_email):
    def responder(request):
        raise httpx.ReadTimeout("private upstream details", request=request)
    external.responder = responder
    response = client.post("/process-email", json=access_email)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "jira_transport_error"
    assert len(external.requests) == 1


def test_missing_jira_credentials_fails_clearly(client, settings, access_email, external):
    settings.jira_email = ""
    response = client.post("/process-email", json=access_email)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "jira_not_configured"
    assert not external.requests


def test_invalid_input(client, external):
    response = client.post("/process-email", json={"emailSubject": "Test", "emailBody": "  ", "senderEmail": "invalid"})
    assert response.status_code == 422
    assert not external.requests


def test_auth_is_required_when_configured(client, settings, access_email):
    from pydantic import SecretStr
    settings.api_auth_token = SecretStr("local-test-auth")
    assert client.post("/process-email", json=access_email).status_code == 401
    response = client.post("/process-email", json=access_email, headers={"Authorization": "Bearer local-test-auth"})
    assert response.status_code == 200


def test_smtp_failure_preserves_created_ticket(client, external, settings, access_email, monkeypatch):
    settings.smtp_host = "smtp.example.com"
    settings.smtp_from = "support@example.com"
    def fail_smtp(*args, **kwargs):
        raise smtplib.SMTPException("private SMTP details")
    monkeypatch.setattr(smtplib, "SMTP", fail_smtp)
    result = client.post("/process-email", json=access_email).json()
    assert result["status"] == "created"
    assert result["ticketKey"] == "KAN-42"
    assert result["confirmation"] == "failed"
    assert result["error"]["code"] == "confirmation_failed"


def test_smtp_sends_key_priority_and_auto_reply_header(client, settings, access_email, monkeypatch):
    settings.smtp_host = "smtp.example.com"
    settings.smtp_user = "support@example.com"
    sent = []
    class FakeSMTP:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def starttls(self, **kwargs): pass
        def login(self, *args): pass
        def send_message(self, message):
            sent.append(message)
            return {}
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    assert client.post("/process-email", json=access_email).json()["confirmation"] == "sent"
    assert sent[0]["To"] == "customer@example.com"
    assert sent[0]["Auto-Submitted"] == "auto-replied"
    assert "KAN-42" in sent[0].get_content()
    assert "High" in sent[0].get_content()


def test_critical_only_for_outages_and_security():
    settings = Settings(_env_file=None)
    for body in ["There is a service outage", "We have a security breach"]:
        outcome = rule_based_triage(EmailRequest(emailSubject="Incident", emailBody=body, senderEmail="user@example.com"))
        assert outcome.priority == "Critical"
    assert settings.dry_run is True


@pytest.mark.parametrize("data", [
    {"issues": None}, {"issues": [None]}, {"issues": [{"key": "KAN-42", "fields": None}]},
    {"issues": [{"key": "KAN-42", "fields": {"summary": None}}]},
    {"issues": [], "nextPageToken": ["invalid"]},
])
def test_malformed_jira_search_fails_clearly(client, external, access_email, data):
    external.responder = lambda request: httpx.Response(200, json=data)
    response = client.post("/process-email", json=access_email)
    assert response.status_code == 502
    assert response.json()["status"] == "failed"
    assert response.json()["error"]["code"] == "jira_invalid_response"


def test_critical_maps_to_highest_in_jira(client, external, access_email):
    access_email["emailBody"] = "There is a security breach"
    response = client.post("/process-email", json=access_email)
    assert response.json()["status"] == "created"
    assert json.loads(external.requests[-1].content)["fields"]["priority"]["name"] == "Highest"
