# Data Model

## Primary entities

### AI use case

Identified by `AI-####`. It owns business context, ownership, governance position, inventory presentation, risk classification, key dates, and references to licenses and evidence.

### License pool

Identified by `LIC-####`. It owns the approved tool name, vendor, capacity, renewal data, funding owner, and list of supported use cases.

### Operational issue

Identified by `ISS-####`. It references exactly one AI use case and owns severity, status, dates, owner, resolution, and escalation flag.

## Relationships

```text
AI use case 1 ───── 0..* operational issues
AI use case 0..* ─ 0..* license pools
AI use case 1 ───── 1 governance record
```

Use cases refer to license IDs with quantities and assignment state. License pools list supported use-case IDs. Validation checks both directions where records exist.

## Separate status dimensions

- `governance.phase` records the canonical lifecycle position.
- `governance.substage` adds execution detail.
- `governance.gate_status` records the current decision state.
- `inventory.bucket` supports portfolio reporting.
- `inventory.operational_status` describes execution health or operational state.
- `record_status` describes whether the data record itself is draft, active, suspended, or retired.

These fields must not be collapsed into a single generic status.
