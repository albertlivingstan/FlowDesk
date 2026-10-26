"""Environment configuration. Blank example values use the documented defaults."""

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_ignore_empty=True, extra="ignore",
        hide_input_in_errors=True,
    )

    dry_run: bool = True
    api_auth_token: SecretStr = SecretStr("")
    llm_api_key: SecretStr = SecretStr("")
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    jira_base_url: str = "https://maker200222.atlassian.net"
    jira_email: str = ""
    jira_api_token: SecretStr = SecretStr("")
    jira_max_retries: int = Field(default=3, ge=0, le=6)
    jira_backoff_seconds: float = Field(default=0.5, ge=0, le=30)
    http_timeout_seconds: float = Field(default=20, gt=0, le=120)
    smtp_host: str = ""
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_user: str = ""
    smtp_pass: SecretStr = SecretStr("")
    smtp_from: str = ""
    smtp_starttls: bool = True
    smtp_ssl: bool = False
    admin_email: str = ""
    imap_host: str = ""
    imap_port: int = Field(default=993, ge=1, le=65535)
    imap_user: str = ""
    imap_pass: SecretStr = SecretStr("")
    imap_folder: str = "INBOX"
    poll_interval_seconds: int = Field(default=60, ge=1)
    process_email_url: str = "http://127.0.0.1:8000/process-email"
    poller_state_path: str = "automation/poller-state.db"
    log_level: str = "INFO"

    @field_validator("jira_base_url", "llm_base_url", "process_email_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        from urllib.parse import urlsplit

        url = urlsplit(value)
        if url.scheme not in {"https", "http"} or not url.hostname:
            raise ValueError("Expected an HTTP(S) URL")
        if url.username or url.password or url.query or url.fragment:
            raise ValueError("URLs must not include credentials, query strings, or fragments")
        return value.rstrip("/")

    @model_validator(mode="after")
    def validate_smtp(self) -> "Settings":
        if self.smtp_ssl and self.smtp_starttls:
            raise ValueError("Use SMTP_SSL or SMTP_STARTTLS, not both")
        return self

    @field_validator("smtp_from", "smtp_user", "admin_email")
    @classmethod
    def validate_mail_header(cls, value: str) -> str:
        if "\r" in value or "\n" in value:
            raise ValueError("Mail configuration cannot contain header line breaks")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
