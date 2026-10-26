# FlowDesk Pro 3.0 — Research and technical development roadmap

## Implemented in this release
- Database-derived 7/30/90/365-day arrival / currently resolved trend charts.
- Interactive sidebar for overview, ticket management, research analytics and email sandbox.
- Ticket state distribution, priority mix, team workloads, hourly activity and category distribution.
- Responsive dashboard, accessible focus indicators, reduced-motion support and interactive ticket drawer.
- Time-based open-ticket SLA *proxy*; these thresholds are demonstrative and not verified contractual SLAs.
- API access checks, ticket audit notes, CSV export, duplicate prevention and PostgreSQL compatibility inherited from v2.

## Research grounding
UiPath's Insights Queue dashboard highlights throughput, completed state, exception breakdown and processing durations. These motivate the chart taxonomy, but FlowDesk DOES NOT yet ingest actual UiPath Orchestrator jobs/queue telemetry: https://docs.uipath.com/insights/automation-cloud/latest/user-guide/queues-template

UiPath supports real-time process/queue/machine monitoring and alerts, subject to feature availability: https://docs.uipath.com/insights/automation-cloud/latest/user-guide/real-time-monitoring-overview

Gmail API push notifications rely on Google Cloud Pub/Sub and Gmail history sync, not solely a POST sent from a browser: https://developers.google.com/workspace/gmail/api/guides/push

## Scientific validation plan — do not invent experimental measurements
1. Assemble consented or synthetic labeled dataset with categories: access, billing, technical support, requests and other.
2. Make 70/15/15 train/development/test stratified split or time-based held-out split; ensure sender/thread leakage is prevented.
3. Compare keyword rules, TF-IDF + logistic regression and compact transformer models. Keep a human-review route for low confidence.
4. Report per-class precision, recall and F1, macro F1, confusion matrix, expected calibration error and abstention rate.
5. Benchmark automated ingestion vs the same manual labeling workflow: seconds per message, errors, retries and API failure recovery.
6. Record bot/job runtime and actual SLA due timestamps before reporting processing time, automation savings or SLA compliance.

## Next engineering milestones (NOT implemented)
- Role-based accounts, SSO/OAuth, API key rotation and per-user audit provenance.
- PostgreSQL Alembic migrations, paging indexes, retention and backup strategy.
- True resolution timestamps, ticket re-open lifecycle, holidays/business-hour calendars and SLA policy database.
- Gmail Pub/Sub or Microsoft Graph change notifications with a durable message queue.
- UiPath Orchestrator event/queue ingestion, failure taxonomy, retry queue and bot health charts.
- Trained NLP model, confidence calibration, PII minimization, encryption and human-approval workflow.

## Important metric caveat
Currently completed tickets are grouped on `updated_at` (last edit) rather than true `resolved_at`. SLA risk compares current age of unresolved tickets to sample thresholds, not actual service contract deadlines. Classifier confidence is a rule score and is not statistically calibrated probability. The demo is NOT production-ready without authentication/authorization and deployment hardening.
