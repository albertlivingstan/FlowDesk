# UiPath integration — Studio Web or Studio Desktop

1. Create an automation in UiPath Studio. Connect a dedicated Gmail mailbox using the Google Workspace integration (follow consent and least-privilege guidance).
2. Use email trigger or **Get Email List** and **For Each Email**.
3. Extract sender email, subject, plain text body, and the provider's stable message ID.
4. Construct JSON: `{"source":"uipath","external_id":"<stable-message-id>","sender":"customer@example.com","subject":"Help","body":"I cannot log in"}`.
5. Call **HTTP Request** POST `https://YOUR-DEPLOYED-API/api/tickets`; headers `X-API-Key: <secure asset value>` and `Content-Type: application/json`.
6. Treat HTTP 201 and the `duplicate: true` response as successful handling. Mark processed / move to completed only on success.
7. On 4xx/5xx or timeouts, log an error and leave the email available for retry. Use a durable message ID to ensure idempotency.
8. Run at least two demonstrations: successful ticket and repeated message (duplicate). Show dashboard and activity history.

**Security:** use UiPath's secure credential assets, never hard-code the API key or store users' passwords inside workflows. Studio Web cannot call a private `localhost` server on your Mac; host the API behind authenticated HTTPS or use an approved secure tunnel for development only. Exact activity names can vary by UiPath package version.
