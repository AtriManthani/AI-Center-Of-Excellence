# Published inventory data

`use-cases.json` is the generated fallback dataset used when live discovery is unavailable. Regenerate it after changing a use-case record:

`python "AI Inventory/scripts/export_inventory.py" --validate`

The dashboard normally discovers approved records directly from `AI Inventory/use-cases`. Never place sensitive information, security findings, personal information, contractual details, network details, vulnerability information, or private comments in this public repository.
