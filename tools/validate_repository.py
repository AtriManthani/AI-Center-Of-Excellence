"""Validate AI COE repository structure and structured records."""

from __future__ import annotations

import sys
from pathlib import Path

from repository_model import (
    ISSUE_DIR,
    LICENSE_DIR,
    ROOT,
    SCHEMA_DIR,
    USE_CASE_DIR,
    duplicate_ids,
    load_configuration,
    load_json,
    load_records,
    validate_cross_references,
    validate_issue_record,
    validate_license_record,
    validate_use_case_record,
)


IGNORED_DIRECTORIES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}


def validate_folder_readmes() -> list[str]:
    errors: list[str] = []
    for directory in sorted(path for path in ROOT.rglob("*") if path.is_dir()):
        if any(part in IGNORED_DIRECTORIES for part in directory.parts):
            continue
        if not (directory / "README.md").exists():
            errors.append(f"{directory.relative_to(ROOT)} is missing README.md")
    return errors


def main() -> int:
    errors: list[str] = []
    try:
        vocab, mapping = load_configuration()
    except Exception as exc:  # noqa: BLE001 - user-facing validator
        print(f"Configuration error: {exc}")
        return 1

    for schema_path in sorted(SCHEMA_DIR.glob("*.json")):
        try:
            load_json(schema_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{schema_path.relative_to(ROOT)}: invalid JSON: {exc}")

    record_sets = []
    for directory in (USE_CASE_DIR, LICENSE_DIR, ISSUE_DIR):
        try:
            record_sets.append(load_records(directory))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{directory.relative_to(ROOT)}: unable to load records: {exc}")
            record_sets.append([])

    use_case_files, license_files, issue_files = record_sets
    for path, record in use_case_files:
        for error in validate_use_case_record(record, vocab, mapping):
            errors.append(f"{path.relative_to(ROOT)}: {error}")
    for path, record in license_files:
        for error in validate_license_record(record, vocab):
            errors.append(f"{path.relative_to(ROOT)}: {error}")
    for path, record in issue_files:
        for error in validate_issue_record(record, vocab):
            errors.append(f"{path.relative_to(ROOT)}: {error}")

    use_cases = [record for _, record in use_case_files]
    licenses = [record for _, record in license_files]
    issues = [record for _, record in issue_files]
    for field, records in (("ai_id", use_cases), ("license_id", licenses), ("issue_id", issues)):
        for duplicate in duplicate_ids(records, field):
            errors.append(f"duplicate {field}: {duplicate}")
    errors.extend(validate_cross_references(use_cases, licenses, issues))
    errors.extend(validate_folder_readmes())

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Repository validation passed: "
        f"{len(use_cases)} use cases, {len(licenses)} licenses, {len(issues)} issues."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
