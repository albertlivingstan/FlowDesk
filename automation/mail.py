import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import Settings
from .logging_utils import event
from .models import EmailRequest, TriageResult


def deliver(message: EmailMessage, settings: Settings) -> str:
    if settings.dry_run or not settings.smtp_host:
        # Log the confirmation content without disclosing the recipient or original mail.
        event("email_logged", dry_run=settings.dry_run,
              subject=str(message["Subject"]), body=message.get_content().strip())
        return "logged"
    if not (settings.smtp_from or settings.smtp_user):
        event("email_failed", reason="smtp_sender_not_configured", level=logging.ERROR)
        return "failed"
    smtp_class = smtplib.SMTP_SSL if settings.smtp_ssl else smtplib.SMTP
    options = {"timeout": settings.http_timeout_seconds}
    if settings.smtp_ssl:
        options["context"] = ssl.create_default_context()
    try:
        with smtp_class(settings.smtp_host, settings.smtp_port, **options) as server:
            if settings.smtp_starttls:
                server.starttls(context=ssl.create_default_context())
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_pass.get_secret_value())
            refused = server.send_message(message)
            if refused:
                event("email_failed", reason="recipient_refused", level=logging.ERROR)
                return "failed"
        event("email_sent")
        return "sent"
    except (smtplib.SMTPException, OSError, ValueError):
        event("email_failed", reason="smtp_unavailable", level=logging.ERROR)
        return "failed"


def send_confirmation(email: EmailRequest, ticket_key: str, triage: TriageResult,
                      settings: Settings, *, duplicate: bool = False) -> str:
    message = EmailMessage()
    message["From"] = settings.smtp_from or settings.smtp_user or "flowdesk@localhost"
    message["To"] = str(email.senderEmail)
    message["Subject"] = f"FlowDesk: {ticket_key} ({triage.priority})"
    message["Auto-Submitted"] = "auto-replied"
    message["X-Auto-Response-Suppress"] = "All"
    action = "added to your existing ticket" if duplicate else "recorded as a support ticket"
    message.set_content(f"Your request has been {action}.\nTicket: {ticket_key}\nPriority: {triage.priority}\n")
    return deliver(message, settings)


def notify_admin(request_id: str, code: str, settings: Settings) -> None:
    event("admin_notification", request_id=request_id, error_code=code, level=logging.ERROR)
    if not settings.admin_email:
        return
    message = EmailMessage()
    message["From"] = settings.smtp_from or settings.smtp_user or "flowdesk@localhost"
    message["To"] = settings.admin_email
    message["Subject"] = "FlowDesk automation needs attention"
    message["Auto-Submitted"] = "auto-generated"
    message.set_content(f"Request: {request_id}\nError code: {code}\nCheck the structured service logs.\n")
    deliver(message, settings)
