"""Optional IMAPS poller with a durable local ledger and human-review inbox.

Run: python -m automation.poller
Inspect reviews: python -m automation.poller --list-reviews
"""

import argparse
import email.policy
import imaplib
import json
import os
import sqlite3
import time
from email import message_from_bytes
from email.utils import parseaddr
from pathlib import Path

import httpx
from pydantic import ValidationError

from .config import Settings, get_settings
from .logging_utils import configure_logging, event
from .models import EmailRequest, ProcessResult
from .triage import clean_text


def open_ledger(path: str) -> sqlite3.Connection:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        fd = os.open(target, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(fd)
    ledger = sqlite3.connect(target)
    ledger.execute("""CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY, status TEXT NOT NULL,
        payload TEXT NOT NULL, result TEXT NOT NULL,
        recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    ledger.commit()
    return ledger


def parse_email(raw: bytes) -> EmailRequest:
    message = message_from_bytes(raw, policy=email.policy.default)
    part = message.get_body(preferencelist=("plain", "html"))
    body = part.get_content() if part else ""
    return EmailRequest(
        emailSubject=str(message.get("Subject", "")), emailBody=clean_text(body),
        senderEmail=parseaddr(str(message.get("From", "")))[1],
        receivedAt=str(message.get("Date", ""))[:80] or None,
    )


def poll_once(settings: Settings, client: httpx.Client, ledger: sqlite3.Connection) -> None:
    with imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port,
                          timeout=settings.http_timeout_seconds) as mailbox:
        mailbox.login(settings.imap_user, settings.imap_pass.get_secret_value())
        status, _ = mailbox.select(settings.imap_folder)
        if status != "OK":
            raise RuntimeError("IMAP folder could not be selected")
        _, validity = mailbox.response("UIDVALIDITY")
        epoch = (validity[0] or b"unknown").decode()
        status, data = mailbox.uid("search", None, "UNSEEN")
        if status != "OK":
            raise RuntimeError("IMAP search failed")
        for uid in (data[0] or b"").split():
            identity = json.dumps([settings.imap_host, settings.imap_user,
                                   settings.imap_folder, epoch, uid.decode()])
            known = ledger.execute("SELECT status FROM messages WHERE message_id = ?", (identity,)).fetchone()
            if known:
                mailbox.uid("store", uid, "+FLAGS", "(\\Seen)")
                continue
            # BODY.PEEK avoids marking messages read before processing has succeeded.
            status, chunks = mailbox.uid("fetch", uid, "(BODY.PEEK[])")
            if status != "OK":
                continue
            raw = next((chunk[1] for chunk in chunks if isinstance(chunk, tuple)), None)
            if raw is None:
                continue
            try:
                message = message_from_bytes(raw, policy=email.policy.default)
                auto_submitted = str(message.get("Auto-Submitted", "no")).lower()
                if auto_submitted != "no":
                    payload, result, result_status = {}, {"reason": "automatic_message"}, "ignored"
                else:
                    request = parse_email(raw)
                    headers = {}
                    if settings.api_auth_token.get_secret_value():
                        headers["Authorization"] = f"Bearer {settings.api_auth_token.get_secret_value()}"
                    response = client.post(settings.process_email_url, json=request.model_dump(mode="json"), headers=headers)
                    response.raise_for_status()
                    outcome = ProcessResult.model_validate(response.json())
                    if outcome.status == "failed":
                        event("poller_processing_failed", request_id=outcome.requestId)
                        continue
                    result_status = outcome.status
                    # Persist review input before marking it read; normal results retain no mail body.
                    payload = request.model_dump(mode="json") if result_status == "needs_review" else {}
                    result = outcome.model_dump(mode="json")
                    if result_status != "needs_review":
                        result.pop("triage", None)
                ledger.execute("INSERT INTO messages (message_id, status, payload, result) VALUES (?, ?, ?, ?)",
                               (identity, result_status, json.dumps(payload), json.dumps(result)))
                ledger.commit()
                mailbox.uid("store", uid, "+FLAGS", "(\\Seen)")
                event("poller_processed", status=result_status)
            except (httpx.HTTPError, ValidationError, ValueError, UnicodeError):
                event("poller_message_deferred", reason="invalid_mail_or_service_unavailable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-reviews", action="store_true")
    args = parser.parse_args()
    settings = get_settings()
    configure_logging(settings)
    with open_ledger(settings.poller_state_path) as ledger:
        if args.list_reviews:
            for row in ledger.execute("SELECT recorded_at, payload, result FROM messages WHERE status = 'needs_review'"):
                # Explicit operator inspection, never emitted by the background logger.
                print(json.dumps({"recordedAt": row[0], "email": json.loads(row[1]), "result": json.loads(row[2])}))
            return
        if not all((settings.imap_host, settings.imap_user, settings.imap_pass.get_secret_value())):
            raise SystemExit("Set IMAP_HOST, IMAP_USER and IMAP_PASS before starting the poller.")
        if settings.dry_run:
            raise SystemExit("The poller marks real mail as seen. Set DRY_RUN=false to enable mailbox polling.")
        with httpx.Client(timeout=settings.http_timeout_seconds, follow_redirects=False) as client:
            while True:
                try:
                    poll_once(settings, client, ledger)
                except (imaplib.IMAP4.error, OSError, RuntimeError):
                    event("poller_retry", reason="imap_unavailable")
                time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
