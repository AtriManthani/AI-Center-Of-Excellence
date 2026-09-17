# Maintainer Guide

## Validate the repository

```text
python tools/validate_repository.py
python -m unittest discover -s tests -v
python tools/generate_dashboard.py --check
```

## Add a record

1. Copy the appropriate template from `shared/templates/`.
2. Replace placeholders with approved values.
3. Save it under the correct `inventory/data/` folder using its permanent ID.
4. Add or update the governed use-case directory when applicable.
5. Run validation.
6. Generate the dashboard with `python tools/generate_dashboard.py`.
7. Review the diff and supporting evidence before committing.

## Change a schema or vocabulary

1. Record the reason and affected consumers.
2. Update the schema version when compatibility changes.
3. Update templates, examples, tests, mappings, and documentation together.
4. Define a migration for existing records.
5. Obtain content-steward review.

## Prepare for transfer

Review repository visibility, access, commit history, secrets, sensitive content, open decisions, actions permissions, branch rules, ownership, and external links before moving the repository into a City-managed organization.
