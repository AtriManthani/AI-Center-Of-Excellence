# Inventory scripts

`export_inventory.py` validates every `status.json` record, including the simple current-phase step sequence, and builds the public-safe fallback dataset at `data/use-cases.json`.

The live dashboard discovers approved use-case records directly from this repository, so filename or folder changes do not require a dashboard redesign.
