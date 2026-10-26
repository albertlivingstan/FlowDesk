# Studio Web: Intelligent Email-to-Ticket

Use the **BPMN import route** for this repository's `content/new.bpmn#manualTrigger1` entry point. The newer **Maestro Flow** canvas uses a different node format; the final section explains how to build the equivalent Flow. A BPMN diagram imports into the BPMN designer, not directly into the Flow canvas. Both run on Maestro, as described in [UiPath's modeler guidance](https://docs.uipath.com/maestro/automation-cloud/latest/user-guide/ways-to-build-with-maestro).

This repo contains portable BPMN, not tenant-specific connection IDs or signed-in integrations. Complete these steps in your own tenant. Labels may vary slightly with the tenant's connector catalog; use the listed operation and field meanings when a connector has been renamed.

## 1. Create Gmail/Outlook and Jira connections

1. Sign in to **UiPath Automation Cloud**, select your organization and tenant, then open **Integration Service**.
2. Select **Connectors**, search **Google Workspace** (or **Gmail** in older catalogs), open the connector and select **Connect** / **Add connection**.
3. Sign in to the dedicated support Google account, grant the requested mail read/send permissions, name the connection `FlowDesk Support Mail`, and save it. For Microsoft mail, repeat with **Microsoft 365** / **Microsoft Outlook 365**, sign in to the support account, and grant the mailbox permissions instead. Only one email provider is needed.
4. In **Connectors**, search **Jira** / **Atlassian Jira**, select **Connect**, then choose **Basic** authentication.
5. Enter **Site URL** `https://maker200222.atlassian.net`, **Username** = your Atlassian email, **API token** = the token generated in Atlassian account security. Name it `FlowDesk Jira` and save. OAuth sign-in is also supported by the connector. Keep the token in the connection, never a workflow expression. See [Jira connection authentication](https://docs.uipath.com/integration-service/automation-cloud/latest/user-guide/uipath-atlassian-jira-authentication).
6. Confirm both connections show connected/valid. The Jira account needs Browse Projects, Create Issues and Add Comments in KAN; configure Task and the priority scheme. Do not edit KAN-1, KAN-2 or KAN-3.

## 2. Import the BPMN and retain the entry point

1. Open **Studio Web → Cloud Workspace → Create New → Maestro BPMN**. If your Studio Web supports Local Workspace solutions, open your existing UiPath solution there instead.
2. Open **Project Explorer**, select **+ → Import** (or the project's context menu → **Import agentic process**), choose `content/new.bpmn`. Studio Web supports importing standard BPMN 2.0 files. See [creating/importing an agentic project](https://docs.uipath.com/studio-web/automation-cloud/latest/user-guide/creating-an-agentic-project).
3. Open `new.bpmn`. Confirm **AI Triage**, the three routing branches, **Human Review**, **Create Jira Ticket**, **Send Confirmation Email**, and the **Notify Admin** boundary path render.
4. Select the start event. Its system ID must remain `manualTrigger1`; do not rename process ID `EmailToTicket`. The repository manifest retains uniqueId `1b957bb9-2a32-47bb-99b8-2a8d891d7d83` and filePath `content/new.bpmn#manualTrigger1`. Studio Web manages its cloud solution metadata separately.
5. Open **Data Manager** and add the following inputs: `emailSubject`, `emailBody`, `senderEmail` (String, required), `receivedAt` (String, optional).
6. Add outputs `isTicket` (Boolean), `ticketKey`, `ticketUrl`, `status` (String). Add working variables `confidence` (Number), `category`, `priority`, `summary`, `description` (String). Initialize ticketKey/ticketUrl to empty strings. Select variables through the picker rather than typing guessed connector paths.

Importing the diagram does not bind runtime implementations. In BPMN, select a node, open the **Properties** wrench, set **Implementation**, and map its input/output values. [UiPath's property configuration reference](https://docs.uipath.com/maestro/automation-cloud/latest/user-guide/properties-panel) describes these mappings and task retries.

## 3. Replace the Manual trigger with Email received

1. On the imported start event, select **Change element → Message start event**. Keep the existing system ID `manualTrigger1`.
2. Open **Properties → Implementation**, select **Wait for connector event**.
3. Choose your Gmail/Google Workspace or Microsoft 365 connector, then connection `FlowDesk Support Mail`.
4. Choose **Email received** / **New email received**, select **INBOX**, and configure any recipient/folder filters. Ignore automatically submitted messages and the support mailbox's own replies to prevent loops.
5. Map the trigger's subject to `emailSubject`, plain-text body to `emailBody`, sender address to `senderEmail`, and received timestamp to `receivedAt`. Some providers return sender as an object: choose its email-address field rather than display name. If only an email ID is emitted, insert the provider's **Get Email** action and map its output instead.
6. Save the changes in the cloud solution. Keep the committed manifest/path unchanged; the supplied local start ID is preserved. During development you can retain a temporary manual trigger in the cloud copy and remove it before deployment.

## 4. Configure AI Triage and the gateway

For BPMN, create a reusable agent first:

1. In Studio Web choose **Create New → Agent**, name it `FlowDesk Support Triage`.
2. Open the Agent node's **Prompt** panel. Paste this system prompt exactly:

```text
You are a support triage assistant. Return ONLY JSON: is_ticket (bool), category (Bug|Billing|Access|Feature Request|General), priority (Low|Medium|High|Critical), summary (max 80 chars), description (cleaned-up request), confidence (0-1). Mark newsletters, spam and out-of-office as is_ticket=false. Use Critical only for outages or security issues.
```

3. In **Schema / Data Manager**, add string inputs `emailSubject`, `emailBody`; put both input chips in the user prompt, clearly identified as email content to classify.
4. Add typed outputs `is_ticket` Boolean, `category` String, `priority` String, `summary` String, `description` String, `confidence` Number. In their descriptions constrain the enums above, summary length ≤80 and confidence 0–1. Choose an available model in the LLM node and temperature 0 when supported. Give this classifier no Jira/mail tools. See [agent authoring in Studio Web](https://docs.uipath.com/agents/automation-cloud/latest/user-guide/building-an-agent-in-studio-web).
5. Test the agent with the four files in `samples/`, then **Publish** it to the same tenant/folder.
6. Return to the BPMN. Select **AI Triage → Properties → Implementation → Start and wait for agent**, choose `FlowDesk Support Triage`, and bind its two inputs.
7. Under **Outputs → Response**, map `is_ticket` to process variable `isTicket`; map category, priority, summary, description and confidence to same-named variables. Explicit output mappings are required; see [agent task configuration](https://docs.uipath.com/maestro/automation-suite/2.2510/user-guide/using-agents-in-maestro).
8. Validate the output before using it: only the listed enum values, actual Boolean, finite 0–1 confidence, and a nonempty summary of at most 80 characters. Invalid/unavailable LLM output should invoke the rule classifier through an API workflow, or use the whole-service HTTP alternative below. A standalone UiPath agent does not automatically run the Python fallback.
9. Select **Support request? → Conditions**. Use the expression editor and variable picker to configure:

| Branch | BPMN expression with process variables |
| --- | --- |
| Ignored | `vars.isTicket === false` |
| Automatic | `vars.isTicket === true && vars.confidence >= 0.7` |
| Human Review | `vars.isTicket === true && vars.confidence < 0.7` |

The portable XML uses bare variable names. Rebind these expressions to the designer's process-variable context (`vars`) on import. Set the **Ignored** end output values to false, empty ticket key/URL, and `ignored`.

## 5. Configure Human Review

1. Select **Human Review → Properties → Implementation → Create action app task**. Select/create an Action App form and assign an authorized reviewer in Action Center.
2. Include sender, subject, body, category, priority, summary, description and confidence. Require the reviewer to correct the fields and explicitly approve before completing this task.
3. Map corrected fields back to the process variables. Set `status=needs_review` while the process waits.
4. Connect completed approval to **Ready to create** (the existing path). To reject with this supplied model, cancel the process in Maestro instead of completing the approval task. For a production reject button, add an approval decision gateway and rejected end path; a completed task on the current path authorizes creation.
5. Use the common Jira/confirmation nodes for approved and automatic requests. Never set a fake high confidence on an unreviewed request just to bypass the review branch.

The Python endpoint returns `needs_review` without creating an issue. It does not wait for an Action Center action or expose an approval bypass endpoint. Its caller owns review persistence; the optional IMAP poller persists such requests locally.

## 6. Map Jira creation, duplicates, confirmation and errors

Use a Studio Web API function/workflow as the implementation behind **Create Jira Ticket** when you need duplicate search + conditional comment/create within this one BPMN service task:

1. Add an **API function** project/item in the solution. Add inputs summary, description, category, priority, senderEmail, receivedAt; outputs ticketKey and ticketUrl.
2. In the API designer select **+**, search **Jira → Search issues by JQL**, choose `FlowDesk Jira`. Filter `project = KAN AND created >= -24h AND key NOT IN ("KAN-1", "KAN-2", "KAN-3")`, optionally adding a safely escaped summary token. Follow all result pages and compare full summary text after whitespace/case normalization. Use `/rest/api/3/search/jql` through the Jira HTTP Request action if the search activity uses an obsolete endpoint.
3. Add an **If**: an exact summary match with an allowed KAN key calls **Jira → Add Comment**, includes the incoming request and reporter, and returns that issue key. Independently reject KAN-1/2/3 from the update path. Otherwise add **Jira → Create Issue** and map:

| Create Issue field | Value |
| --- | --- |
| Connection | FlowDesk Jira |
| Project | KAN |
| Issue type | Task |
| Summary | triage/reviewer `summary`, max 80 characters |
| Description | `description` plus two newlines and `Reported by: ` + senderEmail |
| Labels | one label: category; replace space with `-` for Feature-Request |
| Priority | Critical→Highest, High→High, Medium→Medium, Low→Low |

4. Select Project and Issue type before filling dynamic fields. If the connector exposes a description text box, use its normal text value; if it exposes the raw REST body, build the ADF document shown in `automation/jira.py`. The official [Create Issue activity reference](https://docs.uipath.com/activities/other/latest/integration-service/uipath-atlassian-jira-create-issue) explains dynamic fields. **Insert Record → Issue** is the connector's generic equivalent when Create Issue is unavailable.
5. Map the returned **Key** to ticketKey and build `https://maker200222.atlassian.net/browse/` + ticketKey as ticketUrl. Publish the API function; bind **Create Jira Ticket** to that API implementation and map inputs/outputs. Configure bounded retries for 429/5xx in the API function, with exponential delay and Retry-After; do not retry ambiguous transport writes blindly.
6. Select **Send Confirmation Email**. Bind an email connector action directly if supported, or an API function containing **Reply to Email** / **Send Email** using `FlowDesk Support Mail`. For Reply use the original message ID; for Send use senderEmail as **To**. Subject: `FlowDesk: <ticketKey> (<priority>)`. Body: `Your request has been recorded. Ticket: <ticketKey>. Priority: <priority>.` Set Auto-Submitted to auto-replied when custom headers are supported.
7. Set the **Ticket created** end outputs: isTicket=true, ticketKey, ticketUrl, status=`created`. Handle delivery failure by logging/notifying admin while retaining the saved key. Do not create a second Jira issue to retry email.
8. Select the attached **Jira error** boundary, configure it to catch errors from Create Jira Ticket, and preserve its connection to **Notify Admin**. Bind Notify Admin to a mail/API action addressed to your admin, with the process ID and safe error code only. Also write a log event if delivery fails.
9. Configure the **Failed** end outputs: isTicket=true, empty ticketKey/ticketUrl, status=`failed`. A timed-out Jira write may need operator reconciliation before another run.

## 7. HTTP Request alternative (fastest end-to-end demo)

This alternative delegates triage, duplicate checking, Jira creation, and confirmation to the fallback API. Use it **instead of** the native business-action nodes for that branch so one message has one owner for Jira writes and email delivery.

1. Run the service locally with `make demo`, verify the sample curl, then deploy it behind authenticated HTTPS reachable from UiPath. Studio Web debug runs in UiPath Cloud; `http://localhost:8000` on your Mac is unreachable from there.
2. Set `API_AUTH_TOKEN` in the service's secret store and restart it. Store the same token in a secure UiPath connection/credential, not literal workflow text.
3. In Maestro Flow, select the trigger's **+ → Tool → HTTP Request**. Set ID `processEmail1`, Method **POST**, URL `https://YOUR-SERVICE/process-email`, Authentication **Manual authentication** (or your configured authenticated connection). In BPMN, bind a service task to an API function containing the HTTP Request activity.
4. Add header **Content-Type: application/json** and **Authorization: Bearer <secure credential value>**. Build the body as an object with the four mapped variables, not string concatenation:

```json
{
  "emailSubject": "<trigger subject>",
  "emailBody": "<plain-text body>",
  "senderEmail": "<sender address>",
  "receivedAt": "<received timestamp>"
}
```

5. For Flow, the parsed JSON response is `$vars.processEmail1.output.body` and HTTP code is `$vars.processEmail1.output.code` (use the output picker for your node). Map isTicket, ticketKey, ticketUrl and status directly from body. Add decisions on status: ignored→End, needs_review→Human task with stored input/triage, created→End, failed→Notify Admin→Failed. Route HTTP errors to the same error path. See [HTTP node configuration and outputs](https://docs.uipath.com/getting-started/other/latest/developer-guide/maestro-flow-price-watch-build).
6. Do not send a second confirmation on `created`; the service sends/logs it. Do not retry a needs_review response as though it were a transient failure. Approval must use corrected fields in the native Jira task or manual Jira handling; resubmitting the same vague email cannot approve it.
7. Keep DRY_RUN=true for the first cloud demonstration. For real tickets, set DRY_RUN=false and the backend Jira/SMTP credentials. The HTTP route uses backend credentials; it does not inherit UiPath's Jira/mail connections automatically.

## 8. If your tenant uses the node-based Maestro Flow canvas

1. Choose **Create New → Maestro Flow**; select **Manual Trigger → Change trigger**, search your mail connector's **Email received**, choose the connection and INBOX. Connector triggers can also be added from the bottom node palette. See [trigger behavior](https://docs.uipath.com/maestro/automation-cloud/latest/user-guide/triggers).
2. Add a **Transform** node if needed to extract sender/subject/body from the trigger. Set node IDs deliberately so later expressions can use the variable picker consistently.
3. For the native route, select **+ → Agent → Autonomous Agent**, name it **AI Triage**, ID `aiTriage`. Choose the model, paste the exact prompt above into **System prompt**, bind the email content in the user prompt/input, and declare the six typed outputs. Do not use a Conversational Agent for unattended email.
4. Add **Control → Decision** with `$vars.aiTriage.output.is_ticket === false`: true→Ignored End. False→another Decision checking `$vars.aiTriage.output.confidence >= 0.7`: true→Jira route, false→**Human task → Quick Form** / **Action App**. Require approval and corrected fields, then merge into the same Jira route.
5. Add connector/API nodes for duplicate lookup/comment/create and email confirmation with the mappings above. Add the Jira node's error output to Notify Admin→Failed. Flow uses error handles; the imported BPMN uses its boundary error event.
6. Alternatively add just the HTTP Request node from section 7 after the mail mapping and route its returned status. This is the shortest path to the fully implemented fallback behavior.

## 9. Debug, publish, deploy

1. Save the solution and resolve designer validation errors: task bindings, input/output mappings, conditions, connection permissions and reviewer assignment.
2. Select **Debug**. For manual testing, supply a sample input from `samples/`. With an email trigger, send controlled messages to the support inbox. Verify Access/High creation, Feature Request/Low, ignored newsletter and the human-review wait. Use dry-run HTTP or connector mocks for the first test; Debug executes real API calls when live connections are bound.
3. In the run trace, inspect the six triage fields, chosen branch, issue key and final status. Simulate Jira failure with a mocked connector/API response; verify Notify Admin/Failed. Verify duplicate handling with the same newly created summary and confirm protected issues are never updated.
4. Select **Publish** in the top toolbar; enter a name/description, select **Orchestrator Personal Workspace Feed** for a personal demo or **Tenant Processes Feed** for shared use, choose version, then **Publish**.
5. Personal-workspace Flow publishing automatically deploys. For the tenant feed, go to **Orchestrator → target folder → Automations → Add process**, choose the package/version, complete connection/requirements settings and select **Create**. Recheck runtime connection bindings and reviewer access. Follow [UiPath's publish/deploy instructions](https://docs.uipath.com/studio-web/automation-cloud/latest/user-guide/publishing-and-deploying-a-maestro-flow).
6. Enable/check the deployed email trigger; send one controlled support email. Confirm the Jira key in the reply and monitor the process instance in Maestro. Keep credentials out of screenshots and exported project files.

Repository work does not sign in, import a cloud solution, publish, or run live connector operations. Those account/tenant steps are the remaining manual actions.
