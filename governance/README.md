# AI Governance

## Purpose

This area tracks each AI use case from initial opportunity through monitoring and closeout. It operationalizes the Governance Playbook through consistent phases, decision gates, responsibilities, artifacts, and evidence.

The Governance Playbook is currently a draft. This area must preserve unresolved decisions instead of presenting them as final policy.

## Canonical lifecycle

| Phase | Primary purpose |
| --- | --- |
| Opportunity Identification | Capture the problem, expected benefit, current process, stakeholders, and AI appropriateness. |
| Opportunity Qualification | Evaluate high-level feasibility, cost and benefit, risk level, and acceptable risk. |
| Opportunity Prioritization | Compare qualified opportunities, confirm capacity and budget, assess technical feasibility, and decide build or buy. |
| Solution Design | Define data, model, security, architecture, risk controls, KPIs, resources, and schedule. |
| Solution Development | Build or configure the solution, prepare data, train users, and validate outputs iteratively. |
| Solution Testing | Complete developer testing, business testing, production pilot, and trustworthy-AI verification. |
| Solution Deployment | Complete change management, monitoring preparation, inventory registration, approval, and production release. |
| Solution Monitoring & Improvement | Monitor feedback, access, consumption, cost, performance, model changes, and emerging risks. |
| Solution Closeout | Address contractual obligations, downstream impacts, stakeholder notice, data retention, and decommissioning. |

Each phase must have an explicit state, responsible owner, required artifacts, and gate outcome. A use case does not advance merely because work has started in the next phase.

## Use-case records

The planned record pattern is:

```text
governance/use-cases/AI-0001-short-name/
├── README.md
├── metadata.yaml
├── identification/
├── qualification/
├── prioritization/
├── design/
├── development/
├── testing/
├── deployment/
├── monitoring/
└── closeout/
```

Only create this structure when the first use cases are migrated. Every created folder must include a README or an equivalent index explaining its contents.

## Minimum governance metadata

A use-case record should eventually identify:

- Permanent AI ID and name
- Requesting department, sponsor, owner, and AI COE contact
- Problem statement and intended users
- Business value and success measures
- Governance phase, substage, and gate state
- Priority, risk tier, data sensitivity, and build/buy decision
- Platform, vendor, model, and license dependencies
- Required reviewers and recorded decisions
- Monitoring owner, cadence, and escalation route
- Closeout outcome and date when applicable

## Gate states

Gate terminology will be finalized before automation. A proposed working vocabulary is `Draft`, `Ready for Review`, `Approved`, `Approved with Conditions`, `Deferred`, and `Not Approved`.

## Responsibilities

The draft playbook assigns activities across the AI Governance Council, AI COE, Data Governance, Cybersecurity, Applications, Infrastructure, UAI, AI Leads, platform owners, and department leadership. The consolidated decision-point RACI and the monitoring/closeout assignments remain incomplete and must not be inferred as final.

## Connection to inventory

Governance owns the lifecycle decision. Inventory presents that decision through portfolio and operational views. The mapping between the two belongs in `shared/` so the same rule is used everywhere.

## Evidence handling

Store sanitized governance artifacts here when approved. Sensitive evidence should remain in an authorized system and be represented by a controlled link or reference, not copied into GitHub.
