# Repository Architecture

## Context

The AI COE is being developed in one personal GitHub repository before a future decision about City organization ownership and separate repositories.

## Components

```text
program ─────────────── consumes approved rollups
   ▲
   │
inventory ◄──────────── reflects governance decisions
   ▲                         │
   │                         ▼
dashboard                governance
   ▲                         │
   └──────── shared standards┘
```

`shared/` supplies schemas, vocabularies, and mappings. `.github/` supplies contribution and validation automation. `tools/` validates records and generates outputs.

## Source-of-truth boundaries

- Governance lifecycle and decisions: `governance/`
- Portfolio, license, and operational records: `inventory/data/`
- Shared definitions: `shared/`
- Executive reporting: `program/`
- Generated current-state view: `inventory/dashboard/`

## Automation boundary

Automation may validate, calculate, and present approved data. It must not make a governance decision, assign risk acceptance, or infer an approval from file placement.

## Future repository split

The top-level `program`, `governance`, and `inventory` areas avoid cross-owned files so they can later be extracted while preserving history. Shared assets must then become a versioned shared package or be copied with an explicit synchronization process. Cross-repository automation should use a GitHub App rather than a personal token.
