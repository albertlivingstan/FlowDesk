"""Strict, validated LLM output with a conservative offline classifier."""

import json
import re
from html import unescape
from html.parser import HTMLParser

import httpx
from pydantic import ValidationError

from .config import Settings
from .logging_utils import event
from .models import EmailRequest, TriageResult

SYSTEM_PROMPT = (
    "You are a support triage assistant. Return ONLY JSON: is_ticket (bool), "
    "category (Bug|Billing|Access|Feature Request|General), "
    "priority (Low|Medium|High|Critical), summary (max 80 chars), "
    "description (cleaned-up request), confidence (0-1). "
    "Mark newsletters, spam and out-of-office as is_ticket=false. "
    "Use Critical only for outages or security issues."
)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"p", "br", "div", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        if tag in {"p", "div", "li"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def clean_text(value: str) -> str:
    if re.search(r"</?(?:html|body|p|div|br|span|a|script|style)\b", value, re.I):
        parser = TextExtractor()
        parser.feed(value)
        value = "".join(parser.parts)
    value = unescape(value)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def has(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.I))


def rule_based_triage(email: EmailRequest) -> TriageResult:
    subject = clean_text(email.emailSubject)
    body = clean_text(email.emailBody)
    text = (subject + "\n" + body).lower().replace("’", "'")
    summary = re.sub(r"\s+", " ", subject or body or "Support request")[:80]
    description = body or subject or "No readable request; manual review required."
    category, priority, confidence = "General", "Medium", 0.45
    ignored = has(text, r"\b(spam|newsletter|unsubscribe|out[ -]of[ -]office|automatic reply|auto[ -]reply|"
                       r"buy now|limited time offer|lottery|casino|win cash|claim your prize|free money)\b")
    if ignored:
        return TriageResult(is_ticket=False, category="General", priority="Low",
                            summary=summary, description=description, confidence=0.98)
    if has(text, r"\b(outage|security (?:incident|breach)|data breach|ransomware|all (?:users|systems) (?:are )?down)\b"):
        category, priority, confidence = "Bug", "Critical", 0.95
    elif has(text, r"\b(log[ -]?in|sign[ -]?in|password|locked out|access denied|mfa|permission)\b"):
        category, priority, confidence = "Access", "High", 0.93
    elif has(text, r"\b(please add|feature request|dark mode|could you add|enhancement|would like .+feature)\b"):
        category, priority, confidence = "Feature Request", "Low", 0.9
    elif has(text, r"\b(invoice|billing|refund|charged|payment|subscription)\b"):
        category, priority, confidence = "Billing", "Medium", 0.87
    elif has(text, r"\b(bug|error|crash(?:es|ed)?|broken|not working|doesn't work|cannot .+|can't .+)\b"):
        category, priority, confidence = "Bug", "Medium", 0.85
    return TriageResult(is_ticket=True, category=category, priority=priority,
                        summary=summary, description=description, confidence=confidence)


def triage(email: EmailRequest, settings: Settings, client: httpx.Client) -> TriageResult:
    if settings.dry_run or not settings.llm_api_key.get_secret_value():
        event("triage_rules", reason="dry_run" if settings.dry_run else "no_llm_key")
        return rule_based_triage(email)
    try:
        response = client.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key.get_secret_value()}"},
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps({
                        "emailSubject": clean_text(email.emailSubject),
                        "emailBody": clean_text(email.emailBody),
                    })},
                ],
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        result = TriageResult.model_validate_json(response.json()["choices"][0]["message"]["content"])
        # A deterministic spam guard also prevents an LLM from promoting obvious auto replies.
        rules = rule_based_triage(email)
        if not rules.is_ticket:
            return rules
        if result.priority == "Critical" and rules.priority != "Critical":
            # Ambiguous Critical classifications require a human rather than automatic escalation.
            result = result.model_copy(update={"confidence": min(result.confidence, 0.69)})
        event("triage_llm", category=result.category, confidence=result.confidence)
        return result
    except (httpx.HTTPError, ValidationError, ValueError, KeyError, IndexError, TypeError):
        event("triage_fallback", reason="llm_unavailable_or_invalid")
        return rule_based_triage(email)
