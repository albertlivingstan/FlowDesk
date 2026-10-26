import json
from email.message import EmailMessage

import httpx

from automation.poller import open_ledger, parse_email, poll_once


def sample_mail(body="I can't log in since this morning"):
    message = EmailMessage()
    message["From"] = 'Customer <customer@example.com>'
    message["To"] = "support@example.com"
    message["Subject"] = "Login problem"
    message.set_content(body)
    return message


class FakeMailbox:
    def __init__(self, raw):
        self.raw = raw
        self.stores = []
        self.fetches = 0

    def __enter__(self): return self
    def __exit__(self, *args): pass
    def login(self, *args): pass
    def select(self, *args): return "OK", []
    def response(self, *args): return "UIDVALIDITY", [b"100"]

    def uid(self, command, *args):
        if command == "search": return "OK", [b"7"]
        if command == "fetch":
            self.fetches += 1
            assert args[1] == "(BODY.PEEK[])"
            return "OK", [(b"metadata", self.raw)]
        if command == "store":
            self.stores.append(args)
            return "OK", []
        raise AssertionError(command)


def test_parse_multipart_email_uses_plain_text():
    message = sample_mail()
    message.add_alternative("<p>HTML alternative</p>", subtype="html")
    result = parse_email(message.as_bytes())
    assert result.senderEmail == "customer@example.com"
    assert result.emailBody == "I can't log in since this morning"


def test_review_persisted_before_seen_and_not_reprocessed(tmp_path, monkeypatch, settings):
    mailbox = FakeMailbox(sample_mail("Something is odd").as_bytes())
    monkeypatch.setattr("automation.poller.imaplib.IMAP4_SSL", lambda *args, **kwargs: mailbox)
    requests = []
    def responder(request):
        requests.append(request)
        return httpx.Response(200, json={"isTicket": True, "status": "needs_review", "requestId": "request-1"})
    with open_ledger(str(tmp_path / "state.db")) as ledger, httpx.Client(transport=httpx.MockTransport(responder)) as client:
        poll_once(settings, client, ledger)
        row = ledger.execute("SELECT status,payload FROM messages").fetchone()
        assert row[0] == "needs_review"
        assert json.loads(row[1])["emailBody"] == "Something is odd"
        assert len(mailbox.stores) == 1
        poll_once(settings, client, ledger)
        assert len(requests) == 1
        assert mailbox.fetches == 1


def test_failed_processing_leaves_unseen(tmp_path, monkeypatch, settings):
    mailbox = FakeMailbox(sample_mail().as_bytes())
    monkeypatch.setattr("automation.poller.imaplib.IMAP4_SSL", lambda *args, **kwargs: mailbox)
    with open_ledger(str(tmp_path / "state.db")) as ledger, httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(502, json={"status": "failed"}))) as client:
        poll_once(settings, client, ledger)
        assert not mailbox.stores
        assert ledger.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0


def test_automatic_replies_are_not_submitted(tmp_path, monkeypatch, settings):
    message = sample_mail()
    message["Auto-Submitted"] = "auto-replied"
    mailbox = FakeMailbox(message.as_bytes())
    monkeypatch.setattr("automation.poller.imaplib.IMAP4_SSL", lambda *args, **kwargs: mailbox)
    def no_calls(request): raise AssertionError("Auto reply must not reach the API")
    with open_ledger(str(tmp_path / "state.db")) as ledger, httpx.Client(transport=httpx.MockTransport(no_calls)) as client:
        poll_once(settings, client, ledger)
        assert len(mailbox.stores) == 1
        assert ledger.execute("SELECT status FROM messages").fetchone()[0] == "ignored"
