# Contributing

This repository is being developed as the working foundation for the AI Center of Excellence.

## Before making a change

1. Identify which area owns the information: `program`, `governance`, `inventory`, `shared`, or `docs`.
2. Check whether the change introduces a new term, status, field, or lifecycle mapping.
3. Use an existing permanent AI use-case ID when the change concerns a known use case.
4. Remove sensitive or restricted information before committing content.

## Change guidelines

- Keep changes focused and explain the reason for them.
- Update the relevant README when a folder's purpose or workflow changes.
- Put reusable definitions and schemas in `shared/` rather than duplicating them.
- Link to authoritative records instead of copying status information between areas.
- Mark proposed policy or unresolved governance content as draft.
- Do not commit secrets, credentials, production data, personal information, or restricted evidence.

## Reviews

During the initial build, changes may be reviewed directly by the repository owner. When the repository moves into a City-managed GitHub organization, branch protection, CODEOWNERS, and formal reviewers should be configured for AI COE, Data Governance, Cybersecurity, and AI Governance Council responsibilities.
