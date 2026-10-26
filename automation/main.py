"""Run from the repository root: uvicorn automation.main:app."""

import secrets
from collections.abc import Iterator
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .jira import JiraError, create_jira_issue
from .logging_utils import configure_logging, event
from .mail import notify_admin, send_confirmation
from .models import EmailRequest, ErrorDetail, ProcessResult
from .triage import triage


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    event("service_started", dry_run=settings.dry_run)
    yield


app = FastAPI(title="FlowDesk Intelligent Email-to-Ticket", version="1.0.0", lifespan=lifespan)


def get_http_client(settings: Settings = Depends(get_settings)) -> Iterator[httpx.Client]:
    with httpx.Client(timeout=settings.http_timeout_seconds, follow_redirects=False) as client:
        yield client


def require_auth(authorization: str | None = Header(default=None),
                 settings: Settings = Depends(get_settings)) -> None:
    token = settings.api_auth_token.get_secret_value()
    if token and not secrets.compare_digest((authorization or "").encode(), f"Bearer {token}".encode()):
        raise HTTPException(status_code=401, detail="A valid Bearer token is required.")


@app.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    return {"status": "ok", "dryRun": settings.dry_run}


@app.post("/process-email", response_model=ProcessResult, dependencies=[Depends(require_auth)],
          responses={502: {"model": ProcessResult, "description": "Jira integration failed"}})
def process_email(email: EmailRequest, settings: Settings = Depends(get_settings),
                  client: httpx.Client = Depends(get_http_client)):
    request_id = uuid4().hex
    assessment = triage(email, settings, client)
    common = {"isTicket": assessment.is_ticket, "triage": assessment,
              "dryRun": settings.dry_run, "requestId": request_id}
    if not assessment.is_ticket:
        event("email_ignored", request_id=request_id)
        return ProcessResult(status="ignored", **common)
    if assessment.confidence < 0.7:
        event("human_review_required", request_id=request_id, confidence=assessment.confidence)
        return ProcessResult(status="needs_review", **common)
    try:
        issue = create_jira_issue(assessment, email, settings, client)
    except JiraError as error:
        notify_admin(request_id, error.code, settings)
        result = ProcessResult(status="failed", error=ErrorDetail(code=error.code, message=error.message), **common)
        return JSONResponse(status_code=502, content=result.model_dump(mode="json"))
    confirmation = send_confirmation(email, issue.key, assessment, settings, duplicate=issue.duplicate)
    error = None
    if confirmation == "failed":
        # The Jira write already succeeded. Preserve the key so callers do not recreate it.
        error = ErrorDetail(code="confirmation_failed", message="Ticket saved, but confirmation delivery failed.")
        notify_admin(request_id, error.code, settings)
    event("email_processed", request_id=request_id, ticket_key=issue.key, duplicate=issue.duplicate,
          confirmation=confirmation)
    return ProcessResult(status="created", ticketKey=issue.key, ticketUrl=issue.url,
                         duplicate=issue.duplicate, confirmation=confirmation, error=error, **common)
