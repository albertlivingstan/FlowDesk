"""Jira v3 integration, exact-summary duplicate checking, and bounded retries."""

import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from uuid import uuid4

import httpx

from .config import Settings
from .logging_utils import event
from .models import EmailRequest, TriageResult

PROJECT = "KAN"
PROTECTED_KEYS = frozenset({"KAN-1", "KAN-2", "KAN-3"})
PRIORITIES = {"Critical": "Highest", "High": "High", "Medium": "Medium", "Low": "Low"}


class JiraError(Exception):
    """Only fixed, safe messages may leave this integration boundary."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class JiraIssue:
    key: str
    url: str
    duplicate: bool = False


def adf(text: str) -> dict:
    return {
        "type": "doc", "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": line}]}
            for line in text.splitlines() if line.strip()
        ] or [{"type": "paragraph", "content": [{"type": "text", "text": "Support request"}]}],
    }


def normalize_summary(value: str) -> str:
    return " ".join(value.split()).casefold()


def retry_delay(response: httpx.Response, attempt: int, settings: Settings) -> float:
    delay = settings.jira_backoff_seconds * 2 ** attempt
    retry_after = response.headers.get("Retry-After", "")
    try:
        delay = max(delay, float(retry_after))
    except ValueError:
        try:
            when = parsedate_to_datetime(retry_after)
            delay = max(delay, (when - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            pass
    return min(60.0, max(0.0, delay) + random.uniform(0, settings.jira_backoff_seconds))


class JiraClient:
    def __init__(self, settings: Settings, client: httpx.Client):
        self.settings = settings
        self.client = client

    def request(self, method: str, path: str, **kwargs) -> dict:
        if not self.settings.jira_email or not self.settings.jira_api_token.get_secret_value():
            raise JiraError("jira_not_configured", "Set JIRA_EMAIL and JIRA_API_TOKEN, or use DRY_RUN=true.")
        for attempt in range(self.settings.jira_max_retries + 1):
            try:
                response = self.client.request(
                    method, f"{self.settings.jira_base_url}{path}",
                    auth=httpx.BasicAuth(self.settings.jira_email, self.settings.jira_api_token.get_secret_value()),
                    headers={"Accept": "application/json", "Content-Type": "application/json"},
                    **kwargs,
                )
            except httpx.RequestError:
                # A timed-out write may already have committed. Do not blindly replay it.
                raise JiraError("jira_transport_error", "Jira request could not be confirmed; check Jira before retrying.") from None
            if response.status_code == 429 or 500 <= response.status_code <= 599:
                if attempt < self.settings.jira_max_retries:
                    delay = retry_delay(response, attempt, self.settings)
                    event("jira_retry", http_status=response.status_code, attempt=attempt + 1, delay=delay)
                    time.sleep(delay)
                    continue
                raise JiraError("jira_unavailable", "Jira is temporarily unavailable; retry after checking the issue history.")
            if not 200 <= response.status_code < 300:
                event("jira_rejected", http_status=response.status_code)
                raise JiraError("jira_rejected", "Jira rejected the request; check credentials, permissions, and field configuration.")
            try:
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("Expected an object")
                return data
            except ValueError:
                raise JiraError("jira_invalid_response", "Jira returned an invalid response; verify the issue before retrying.") from None
        raise AssertionError("Unreachable retry state")

    def find_duplicate(self, summary: str) -> str | None:
        # Jira's summary field supports text search, not exact equality. Use a safe
        # token as the JQL prefilter, then compare full normalized summaries locally.
        words = re.findall(r"[A-Za-z0-9]+", summary)
        terms = [word for word in words if word.lower() not in {"a", "an", "the", "i", "and", "or", "to"}]
        token = max(terms, key=len) if terms else ""
        jql = 'project = "KAN" AND created >= -24h AND key NOT IN ("KAN-1", "KAN-2", "KAN-3")'
        if token:
            jql += f' AND summary ~ "{token}"'
        jql += " ORDER BY created DESC"
        page_token = None
        visited = set()
        while True:
            payload = {"jql": jql, "maxResults": 100, "fields": ["summary"]}
            if page_token:
                payload["nextPageToken"] = page_token
            data = self.request("POST", "/rest/api/3/search/jql", json=payload)
            issues = data.get("issues")
            if not isinstance(issues, list):
                raise JiraError("jira_invalid_response", "Jira search returned invalid issue data.")
            for issue in issues:
                if not isinstance(issue, dict) or not isinstance(issue.get("fields"), dict):
                    raise JiraError("jira_invalid_response", "Jira search returned invalid issue data.")
                key = issue.get("key", "")
                if not isinstance(key, str) or key in PROTECTED_KEYS or not re.fullmatch(r"KAN-[1-9]\d*", key):
                    continue
                found_summary = issue["fields"].get("summary")
                if not isinstance(found_summary, str):
                    raise JiraError("jira_invalid_response", "Jira search returned invalid summary data.")
                if normalize_summary(found_summary) == normalize_summary(summary):
                    return key
            page_token = data.get("nextPageToken")
            if not page_token:
                return None
            if not isinstance(page_token, str):
                raise JiraError("jira_invalid_response", "Jira search returned an invalid page token.")
            if page_token in visited:
                raise JiraError("jira_invalid_response", "Jira search pagination did not advance.")
            visited.add(page_token)

    def create_jira_issue(self, triage: TriageResult, email: EmailRequest) -> JiraIssue:
        if self.settings.dry_run:
            key = f"DRY-{uuid4().hex[:8].upper()}"
            event("jira_dry_run", ticket_key=key, category=triage.category, priority=triage.priority)
            return JiraIssue(key=key, url="")
        description = f"{triage.description}\n\nReported by: {email.senderEmail}"
        if email.receivedAt:
            description += f"\nReceived at: {email.receivedAt}"
        existing = self.find_duplicate(triage.summary)
        if existing:
            # Guard independently of search filters: protected tickets are never mutated.
            if existing in PROTECTED_KEYS:
                raise JiraError("protected_issue", "This issue is protected from automation updates.")
            self.request("POST", f"/rest/api/3/issue/{existing}/comment", json={
                "body": adf(f"Additional support report\n{description}"),
            })
            event("jira_duplicate_commented", ticket_key=existing)
            return JiraIssue(existing, f"{self.settings.jira_base_url}/browse/{existing}", True)
        result = self.request("POST", "/rest/api/3/issue", json={
            "fields": {
                "project": {"key": PROJECT}, "issuetype": {"name": "Task"},
                "summary": triage.summary,
                # Jira labels cannot contain spaces. Keep the category spelling otherwise.
                "labels": [triage.category.replace(" ", "-")],
                "description": adf(description),
                "priority": {"name": PRIORITIES[triage.priority]},
            },
        })
        key = result.get("key", "")
        if not isinstance(key, str) or not re.fullmatch(r"KAN-[1-9]\d*", key) or key in PROTECTED_KEYS:
            raise JiraError("jira_invalid_response", "Jira did not return a valid new KAN issue key.")
        event("jira_created", ticket_key=key)
        return JiraIssue(key, f"{self.settings.jira_base_url}/browse/{key}")


def create_jira_issue(triage: TriageResult, email: EmailRequest, settings: Settings,
                      client: httpx.Client) -> JiraIssue:
    return JiraClient(settings, client).create_jira_issue(triage, email)
