# AI Center of Excellence

This repository is the working home for the City of Cleveland AI Center of Excellence (AI COE). It brings program communication, AI governance, and the AI inventory together while keeping a clear source of truth for each type of information.

The repository is intentionally organized as a monorepo during the design and pilot period. Each major area can be separated into its own repository later without changing its responsibility.

## Repository map

| Area | Purpose | Source of truth for |
| --- | --- | --- |
| [`program/`](program/) | High-level program communication and portfolio reporting | Program status, roadmap, outcomes, risks, and decisions |
| [`governance/`](governance/) | Intake-to-closeout governance for AI use cases | Lifecycle phase, gate decisions, governance artifacts, and approvals |
| [`inventory/`](inventory/) | Structured registry of AI use cases, licenses, issues, and operational state | Inventory records and license capacity |
| [`shared/`](shared/) | Definitions, schemas, mappings, and reusable templates | Cross-area standards |
| [`docs/`](docs/) | Supporting documentation and design decisions | Repository documentation and approved reference material |
| [`.github/`](.github/) | GitHub configuration and automation | Contribution forms, review rules, and validation workflows |

Each area has its own README explaining its scope, audience, ownership, and working conventions.

## Operating model

The three primary areas serve different purposes but share a single use-case identity:

1. A use case is identified and receives a permanent ID such as `AI-0001`.
2. `governance/` tracks the use case through the governance lifecycle and records gate decisions.
3. `inventory/` maintains the portfolio record, operational state, license demand, and related issues.
4. `program/` communicates approved rollups without recreating the underlying governance or inventory data.

One fact should have one owner. Other areas link to or consume that fact rather than maintaining conflicting copies.

## Canonical governance lifecycle

The draft Governance Playbook defines nine lifecycle phases:

1. Opportunity Identification
2. Opportunity Qualification
3. Opportunity Prioritization
4. Solution Design
5. Solution Development
6. Solution Testing
7. Solution Deployment
8. Solution Monitoring & Improvement
9. Solution Closeout

The lifecycle phase is distinct from an inventory reporting bucket. For example, a solution in `Solution Testing` may use the inventory substage `Validation`, `Testing`, or `Pilot`. Keeping these concepts separate preserves governance detail while supporting an executive dashboard.

## Information handling

Do not commit credentials, secrets, resident information, production datasets, sensitive personal information, or confidential vendor material. Store approved metadata and sanitized artifacts here, with links to an authorized system when supporting evidence must remain elsewhere.

The Governance Playbook and AI Inventory materials are drafts. Unresolved terminology, RACI assignments, lifecycle mappings, and license totals must be reconciled before they are treated as approved standards.

## Working conventions

- Use Markdown for human-readable documentation.
- Use structured YAML or JSON for records that require validation or reporting.
- Use the permanent `AI-####` identifier everywhere a use case is referenced.
- Make material changes through a reviewable branch and pull request once collaboration begins.
- Record assumptions and unresolved decisions explicitly; do not silently invent governance policy.
- Keep folder boundaries clean so each primary area can be extracted into a separate repository later.

## Repository capabilities

This repository includes:

- A documented operating model for the program, governance, and inventory areas
- Structured JSON schemas for use cases, licenses, and operational issues
- Canonical vocabularies and governance-to-inventory lifecycle mappings
- Reusable program, governance, and inventory templates
- GitHub issue forms for intake, gate reviews, risks, and monitoring incidents
- Automated validation, consistency checks, tests, and dashboard freshness checks
- A generated inventory dashboard that will populate as approved records are added
- A reconciliation register for decisions that remain unresolved in the source drafts

No City use-case or license records are fabricated. The data directories remain ready for approved records to be migrated.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing a change.

Repository decision rights are described in [`GOVERNANCE.md`](GOVERNANCE.md), and information-handling guidance is in [`SECURITY.md`](SECURITY.md).
