# AI Inventory

## Purpose

This area maintains the structured registry of City AI use cases and the licenses, operational issues, and production information associated with them. It supports portfolio reporting while preserving traceability to governance decisions.

The inventory is a system of record, not only a presentation. Dashboards should be generated from validated inventory data rather than maintained independently.

## Core record types

### Use cases

Each record uses a permanent `AI-####` identifier and describes the use case, department, owner, governance position, inventory bucket, operational state, priority, risk, important dates, and links to governance evidence.

### Licenses

License records capture the approved tool name, purchased capacity, assigned capacity, available capacity, utilization, funding owner, renewal information, and supported use cases. Personally identifiable assignment details should not be stored unless explicitly approved.

### Issues

Operational issues use their own identifier and reference an existing AI use-case ID. They capture issue type, severity, status, discovery date, owner, resolution, and any governance escalation.

## Portfolio views

The analyzed inventory design includes:

- In Progress
- Prioritization
- Priority Backlog
- In Production
- Resolved
- Decommissioned
- Open Issues
- AI License Tracking
- Use cases by department and status

These are reporting views, not replacements for the canonical governance lifecycle.

## Lifecycle mapping

| Governance position | Inventory presentation |
| --- | --- |
| Opportunity Identification or Qualification | Pre-inventory governance pipeline |
| Opportunity Prioritization | Prioritization |
| Solution Design or Development | In Progress |
| Solution Testing | In Progress with Validation, Testing, or Pilot substage |
| Solution Deployment | Moving to Production |
| Solution Monitoring & Improvement | In Production |
| Solution Closeout | Resolved or Decommissioned, based on outcome |

The final inventory-entry point and the meaning of `Resolved` must be confirmed before records are migrated.

## Planned organization

```text
inventory/
├── README.md
├── data/
│   ├── use-cases/
│   ├── licenses/
│   └── issues/
├── schemas/
├── reports/
├── dashboard/
└── archive/
```

Only create these folders as their first content is added, and include a README in every new folder.

## Data-quality rules

Automated validation should eventually confirm that:

- Every ID is unique and correctly formatted.
- Every issue references an existing use case.
- Lifecycle, priority, risk, and status values use approved vocabularies.
- License totals reconcile to their component records.
- Production use cases identify a monitoring owner and monitoring plan.
- Backlogged and decommissioned records include a reason.
- Dates and cross-repository links are valid.

The draft inventory's license totals and its license assumptions require reconciliation with the Governance Playbook before they are imported.

## Ownership

The AI COE maintains the inventory. Governance decisions originate in `governance/`; inventory records reflect those decisions and add portfolio, operational, and license information.
