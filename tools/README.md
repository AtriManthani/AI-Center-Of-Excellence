# Repository Tools

This folder contains dependency-free Python utilities used locally and in GitHub Actions.

- `validate_repository.py` validates structure, JSON, identifiers, vocabularies, lifecycle mappings, cross-record references, required monitoring fields, and license arithmetic.
- `generate_dashboard.py` creates the Markdown inventory dashboard from approved records.
- `repository_model.py` contains shared loading and validation functions.

The tools validate repository consistency; they do not approve use cases or make governance decisions.
