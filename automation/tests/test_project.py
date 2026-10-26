import json
import logging
from pathlib import Path

import pytest
from pydantic import ValidationError

from automation.config import Settings
from automation.logging_utils import RedactingFormatter
from automation.validate_project import validate


def test_entry_point_bpmn_graph_and_di():
    validate()


def test_env_example_covers_every_setting_with_empty_values():
    from dotenv import dotenv_values
    root = Path(__file__).resolve().parents[2]
    values = dotenv_values(root / ".env.example")
    assert {name.upper() for name in Settings.model_fields} <= values.keys()
    assert all(value == "" for value in values.values())


def test_empty_example_values_use_defaults(tmp_path):
    env = tmp_path / ".env"
    env.write_text("DRY_RUN=\nSMTP_PORT=\nLLM_MODEL=\n")
    settings = Settings(_env_file=env)
    assert settings.dry_run is True
    assert settings.smtp_port == 587
    assert settings.llm_model == "gpt-4o-mini"


def test_environment_takes_precedence_over_dotenv(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("DRY_RUN=true\n")
    monkeypatch.setenv("DRY_RUN", "false")
    assert Settings(_env_file=env).dry_run is False


def test_logs_redact_secrets_and_authorization():
    formatter = RedactingFormatter(["example-sensitive-value"])
    record = logging.LogRecord("test", logging.INFO, "", 0,
                              '{"token":"example-sensitive-value","header":"Bearer private-value"}', (), None)
    output = formatter.format(record)
    assert "example-sensitive-value" not in output
    assert "private-value" not in output
    assert "REDACTED" in output
    assert isinstance(json.loads(output), dict)


@pytest.mark.parametrize("value", ["ftp://example.com", "https://user:password@example.com", "https://example.com?token=private"])
def test_config_rejects_credential_bearing_urls(value):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jira_base_url=value)


def test_mutually_exclusive_smtp_modes():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, smtp_ssl=True, smtp_starttls=True)
