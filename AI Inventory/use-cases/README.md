# Use-case records

Each folder represents one permanent AI use case and begins with its ID, for example:

`AI-0001-resident-services-assistant`

Copy `_template`, rename it, and update `status.json` and `governance.json`.

Each use case has nine plainly named phase folders. Upload a public-safe form, review, or supporting file directly into the phase where it belongs. Update the control-ID checklist in that same folder.

Use `status.json` for the leadership summary and current position. Use `governance.json` for phase progress, requirement status, gate decisions, formal reviews, technical risks, decisions, and monitoring. Requirement IDs are defined once in `governance/controls.json`.

Do not create a new use-case folder when the phase or status changes. The same folder follows the use case from Intake through Close.

The repository is currently public. Do not upload internal architecture diagrams, security findings, vulnerabilities, network details, credentials, personal information, or confidential vendor material. Record a public-safe summary such as `Reviewed internally` instead.
