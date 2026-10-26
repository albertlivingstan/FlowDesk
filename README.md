# FlowDesk Pro v2 — Intelligent Email-to-Ticket RPA

A runnable FastAPI/PostgreSQL ticket-management application with rule-based text classification, priority routing, safe deduplication, ticket audit history, filtering, CSV export, a responsive dashboard, optional IMAP inbox polling, and UiPath Studio integration instructions.

## Quick start on macOS / Windows / Linux (SQLite demo)

```bash
cd FlowDesk_Pro_v2
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export API_KEY='your-long-random-key' # Windows PowerShell: $env:API_KEY='your-long-random-key'
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** and enter the same API key at top right. The SQLite database (`flowdesk.db`) is created automatically. This is a local demo, not multi-user production auth.

## PostgreSQL mode

1. Install and start Docker Desktop.
2. `docker compose up -d db`.
3. Set `DATABASE_URL=postgresql+psycopg://flowdesk:flowdesk_dev_password@localhost:5432/flowdesk` and `API_KEY=<strong-secret>` in your shell (or load `.env` explicitly with a shell tool). Alternatively copy `.env.example` to `.env` and launch `uvicorn` with `--env-file .env`.
4. Run `uvicorn app.main:app --reload`.
5. **Avoid committing `.env`.** Replace the sample database credentials before public deployments.

## Test

```bash
pytest -q
```

## Demo API

```bash
curl -X POST http://127.0.0.1:8000/api/tickets \
  -H 'X-API-Key: your-long-random-key' -H 'Content-Type: application/json' \
  -d '{"source":"uipath","external_id":"email-123","sender":"client@example.com","subject":"Urgent: Cannot log in","body":"Password reset is not working."}'
```

Repeat the same request to verify duplicate suppression. The ticket appears in the dashboard. Click it to update status or priority and add notes. Export the queue as CSV.

## Inbox automation options

- **UiPath:** see `uipath/STUDIO_WORKFLOW.md` (workflow instructions; not an exported `.xaml` robot).
- **IMAP optional worker:** `IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD`, `API_KEY`, optional `FLOWDESK_API_URL`; then `python -m app.imap_worker`. Use an app password/OAuth-supported dedicated test account if allowed by the provider. It polls unread emails and marks them read only after successful API delivery. Validate compliance with your organization's email privacy policies.

## Architecture

Email (UiPath or IMAP) → POST /api/tickets → transparent rules baseline → PostgreSQL/SQLite tickets + events → dashboard + CSV reports.

## Honest limitations / production backlog

- Keyword classifier is **not** a trained ML/NLP model; confidence is heuristic, not calibrated probability. Confirm classifications with labeled test data.
- API key is a shared secret; implement SSO/RBAC for multiple users. Browser key entry should only be used on a trusted local development machine.
- Add Alembic migrations, a job queue, structured logs/metrics, rate limits, managed secrets, SLA escalation, email privacy retention/deletion, secure HTTPS hosting, and end-to-end UiPath runs before claiming production readiness.
- IMAP UID stability depends on mailbox UIDVALIDITY; for production deduplication, store UIDVALIDITY or use provider-stable message identifiers.
- The demo does not send outbound customer replies; no emails are sent without separate configuration.

## UiPath assignment demonstration sequence

1. Run `pytest -q` and record test results.
2. Launch the dashboard and create a sample email-derived ticket.
3. Show automatic classification/priority/team and database persistence.
4. Repeat `external_id` through API to demonstrate duplicate prevention.
5. Change ticket status, add a note, and show activity audit trail.
6. Export CSV and explain manual-review handling.
7. Connect the UiPath workflow using the separate guide, then repeat the demo with an actual test email.

**Testing scope:** unit/in-process API tests cover the local SQLite path. PostgreSQL, browser rendering, IMAP provider connections, and actual UiPath Studio execution have not been verified in this environment.

## FlowDesk 3.0 visualization upgrade

The dashboard now includes interactive multi-page navigation, daily arrival/completion chart, donut status mix, team/category/priority progress charts, hourly activity histogram, time-range selection, detail drawer and animated cards. `GET /api/analytics?days=30` provides actual stored-ticket aggregates. Read `RESEARCH_AND_ROADMAP.md` for limitations and further research directions. No illustrative / fabricated KPI values are inserted automatically.
