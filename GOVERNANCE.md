# Repository Governance

## Purpose

This document defines how the AI Center of Excellence repository is maintained while it is hosted as a personal development repository. It does not replace the City AI Governance Playbook or establish City policy.

## Current decision rights

The repository owner is the final approver for changes during the initial build. Subject-matter review should still be requested when a change concerns data governance, cybersecurity, architecture, procurement, legal requirements, departmental operations, or AI Governance Council decisions.

## Content ownership

| Content | Primary steward |
| --- | --- |
| Program reporting | AI COE program management |
| Use-case lifecycle and gates | AI COE with the AI Governance Council |
| Data governance evidence | Data Governance/UAI |
| Security evidence | Cybersecurity |
| Inventory and license registry | AI COE |
| Shared schemas and mappings | AI COE with affected reviewers |
| Repository automation | Repository maintainer |

Named teams and final RACI assignments remain subject to approval in the operating model.

## Change classes

### Routine

Documentation corrections, formatting, and approved record updates may use normal review.

### Controlled

Changes to schemas, lifecycle mappings, enumerated values, gate criteria, or reporting calculations require review from the content steward and must explain migration impact.

### Restricted

Changes that expose sensitive information, weaken validation, alter access controls, or bypass review must not be merged without explicit authorization.

## Decision records

Material repository-design decisions are recorded in `docs/decisions/`. Policy decisions belong in the approved City governance process and may be referenced here after approval.

## Future transition

When the work moves to a City-managed GitHub organization, replace personal ownership with organization teams, least-privilege repository roles, protected branches, required reviewers, and organization-managed automation credentials.
