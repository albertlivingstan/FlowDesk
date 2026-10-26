import httpx
import pytest
from fastapi.testclient import TestClient

from automation.config import Settings, get_settings
from automation.main import app, get_http_client


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch):
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    get_settings.cache_clear()
    # Tests must never reach any real HTTP service, even if a mock is missing.
    def deny_network(*args, **kwargs):
        raise AssertionError("Unexpected real HTTP request in offline tests")
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", deny_network)
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def settings():
    return Settings(_env_file=None, dry_run=False, jira_email="automation@example.com",
                    jira_api_token="test-jira-token", jira_backoff_seconds=0)


@pytest.fixture
def external():
    class External:
        def __init__(self):
            self.requests = []
            self.responder = self.default_response

        def default_response(self, request):
            if request.url.path == "/rest/api/3/search/jql":
                return httpx.Response(200, json={"issues": [], "isLast": True})
            if request.url.path == "/rest/api/3/issue":
                return httpx.Response(201, json={"key": "KAN-42"})
            if request.url.path.endswith("/comment"):
                return httpx.Response(201, json={"id": "10001"})
            raise AssertionError(f"Unexpected mocked path: {request.url.path}")

        def handle(self, request):
            self.requests.append(request)
            return self.responder(request)

    return External()


@pytest.fixture
def client(settings, external):
    app.dependency_overrides[get_settings] = lambda: settings
    def http_client():
        with httpx.Client(transport=httpx.MockTransport(external.handle)) as session:
            yield session
    app.dependency_overrides[get_http_client] = http_client
    with TestClient(app) as api:
        yield api


@pytest.fixture
def access_email():
    return {"emailSubject": "Login problem", "emailBody": "I can't log in since this morning",
            "senderEmail": "customer@example.com"}
