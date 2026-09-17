# ADR-0002: Separate governance and reporting status

**Status:** Accepted
**Date:** 2026-09-17

## Context

The Governance Playbook uses nine lifecycle phases. The Inventory design uses executive buckets and substages that do not map one-to-one to those phases.

## Decision

Store governance phase, governance substage, gate status, inventory bucket, and operational status as distinct fields. Validate allowed combinations through a shared mapping.

## Consequences

- Governance detail is preserved.
- Dashboard views can use simpler labels without redefining the lifecycle.
- Record updates must consider more than one field.
- Automation can identify inconsistent combinations.
