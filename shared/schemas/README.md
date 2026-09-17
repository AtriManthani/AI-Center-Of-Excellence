# JSON Schemas

This folder contains the machine-readable contracts for repository data.

- `use-case.schema.json` defines governed inventory records.
- `license.schema.json` defines license-pool records.
- `issue.schema.json` defines operational issue records.

The local validator performs required-field, vocabulary, cross-record, lifecycle-mapping, and arithmetic checks without external packages. The schemas provide an additional portable contract for editors and future integrations.
