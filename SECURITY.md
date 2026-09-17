# Security and Information Handling

## Reporting a concern

Do not open a public issue containing a vulnerability, credential, personal information, resident information, or confidential evidence. Contact the repository owner through an approved private channel and provide only the minimum information needed to route the concern.

## Prohibited content

Do not commit:

- Passwords, API keys, tokens, certificates, or connection strings
- Resident, employee, or user-level personal information
- Production datasets or unredacted test datasets
- Security-sensitive architecture details that have not been approved for this repository
- Confidential contracts, vendor evidence, or procurement material
- Model prompts, outputs, or logs containing restricted data

## Safe record design

- Store business metadata and sanitized evidence.
- Use controlled links for evidence retained in an approved external system.
- Track license capacity without naming individual assignees unless that use is explicitly approved.
- Use synthetic data in examples and tests.
- Review generated reports before distributing them beyond the authorized audience.

## Automation

Workflows must use least-privilege permissions. Secrets must be provided by GitHub's encrypted secret or environment mechanisms and must never appear in source files, logs, examples, or test fixtures.

## Repository visibility

This scaffold is designed for a private working repository. Before changing visibility or transferring ownership, review all committed content and history for information that should not become broadly accessible.
