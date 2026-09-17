# ADR-0001: Begin with a monorepo

**Status:** Accepted
**Date:** 2026-09-17

## Context

The AI COE needs to develop program, governance, and inventory capabilities before deciding on a City-managed GitHub organization and final repository boundaries.

## Decision

Use one personal repository with clean top-level boundaries for `program`, `governance`, and `inventory`. Maintain shared standards in `shared/` and automate validation centrally.

## Consequences

- The initial system can be designed and tested without cross-repository credentials.
- Shared changes and lifecycle mappings remain atomic.
- Access cannot yet be restricted independently by business area.
- A future split will require a shared-assets and automation strategy.

## Alternatives considered

- Three repositories immediately: deferred until ownership, access, and organization controls are known.
- Nested Git repositories or submodules: rejected because they add coordination and contributor friction without solving the current design need.
