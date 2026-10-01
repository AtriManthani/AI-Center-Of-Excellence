# Inventory scripts

`export_inventory.py` validates each use case's `status.json` and `governance.json` against `governance/controls.json`, then builds the public-safe fallback dataset at `data/use-cases.json`.

Validation covers all nine phases, stable control IDs, gate decisions, dates, formal Cyber/Data/Application/Network/Enterprise reviews, technical risks, decisions, issues, benefits, and monitoring fields.

The live dashboard discovers approved use-case records directly from this repository, so filename or folder changes do not require a dashboard redesign.
