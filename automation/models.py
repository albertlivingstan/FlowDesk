from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Category = Literal["Bug", "Billing", "Access", "Feature Request", "General"]
Priority = Literal["Low", "Medium", "High", "Critical"]


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    emailSubject: str = Field(max_length=998)
    emailBody: str = Field(min_length=1, max_length=100_000)
    senderEmail: EmailStr
    receivedAt: str | None = Field(default=None, max_length=80)

    @field_validator("emailBody")
    @classmethod
    def body_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("emailBody cannot be blank")
        return value


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    is_ticket: bool
    category: Category
    priority: Priority
    summary: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=100_000)
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)

    @field_validator("summary", "description")
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be blank")
        return value


class ErrorDetail(BaseModel):
    code: str
    message: str


class ProcessResult(BaseModel):
    isTicket: bool
    ticketKey: str = ""
    ticketUrl: str = ""
    status: Literal["created", "ignored", "needs_review", "failed"]
    triage: TriageResult | None = None
    duplicate: bool = False
    dryRun: bool = False
    confirmation: Literal["sent", "logged", "failed", "not_requested"] = "not_requested"
    requestId: str
    error: ErrorDetail | None = None
