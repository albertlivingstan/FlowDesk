"""JSON events: never log input mail, HTTP bodies, headers, or raw exceptions."""

import json
import logging
import re
from datetime import datetime, timezone

from .config import Settings

logger = logging.getLogger("flowdesk")


class RedactingFormatter(logging.Formatter):
    def __init__(self, secrets: list[str]):
        super().__init__()
        self.secrets = sorted((s for s in secrets if s), key=len, reverse=True)

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        for secret in self.secrets:
            message = message.replace(secret, "[REDACTED]")
        message = re.sub(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9+/=_\-.]+", r"\1 [REDACTED]", message)
        message = re.sub(
            r"(?i)((?:token|password|api_key|secret)\s*[=:]\s*)[^\s,\"}]+",
            r"\1[REDACTED]", message,
        )
        return message


def configure_logging(settings: Settings) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter([
        settings.api_auth_token.get_secret_value(), settings.llm_api_key.get_secret_value(),
        settings.jira_api_token.get_secret_value(), settings.smtp_pass.get_secret_value(),
        settings.imap_pass.get_secret_value(),
    ]))
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    # HTTP library debug output can contain credential-bearing headers.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def event(name: str, *, level: int = logging.INFO, **fields: object) -> None:
    logger.log(level, json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(), "event": name, **fields,
    }, ensure_ascii=True))
