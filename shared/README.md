# Shared Standards

## Purpose

This area contains definitions and reusable assets that must remain consistent across the AI program, governance process, and inventory.

Content should be placed here only when it has more than one consumer. Area-specific material belongs with the area that owns it.

## Planned content

- Canonical terminology and definitions
- Use-case ID conventions
- Governance-to-inventory lifecycle mappings
- Approved status, priority, risk, and gate vocabularies
- Machine-readable schemas
- Reusable document and record templates
- Shared validation rules
- Naming and date conventions

## Design principles

- Maintain one canonical definition for each shared term.
- Version breaking schema or vocabulary changes deliberately.
- Document both the change and its effect on existing records.
- Prefer enumerated values over free text when data will be filtered or reported.
- Keep presentation labels separate from authoritative lifecycle states.
- Do not place use-case-specific data in this area.

## Proposed ID standard

AI use cases should use a zero-padded permanent identifier in the form `AI-####`, for example `AI-0001`. IDs are never reused, even after a use case is closed or decommissioned.

Issue, decision, and license identifiers will be defined before structured records are introduced.

## Ownership

The AI COE maintains shared standards with review from the appropriate governance, data, security, and technical stakeholders. Draft values must be clearly identified until approved.
