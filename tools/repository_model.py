"""Shared loaders and validation functions for the AI COE repository."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
VOCABULARY_PATH = ROOT / "shared" / "vocabularies" / "vocabularies.json"
MAPPING_PATH = ROOT / "shared" / "mappings" / "lifecycle-mapping.json"
SCHEMA_DIR = ROOT / "shared" / "schemas"
USE_CASE_DIR = ROOT / "inventory" / "data" / "use-cases"
LICENSE_DIR = ROOT / "inventory" / "data" / "licenses"
ISSUE_DIR = ROOT / "inventory" / "data" / "issues"

AI_ID = re.compile(r"^AI-\d{4}$")
LICENSE_ID = re.compile(r"^LIC-\d{4}$")
ISSUE_ID = re.compile(r"^ISS-\d{4}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_records(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    return [(path, load_json(path)) for path in sorted(directory.glob("*.json"))]


def load_configuration() -> tuple[dict[str, Any], dict[str, Any]]:
    return load_json(VOCABULARY_PATH), load_json(MAPPING_PATH)


def _missing(record: dict[str, Any], required: Iterable[str], prefix: str = "") -> list[str]:
    return [f"missing required field {prefix}{key}" for key in required if key not in record]


def _enum(value: Any, allowed: list[str], field: str) -> list[str]:
    return [] if value in allowed else [f"{field} has unsupported value {value!r}"]


def _date(value: Any, field: str, nullable: bool = True) -> list[str]:
    if value is None and nullable:
        return []
    if not isinstance(value, str):
        return [f"{field} must be an ISO date string"]
    try:
        date.fromisoformat(value)
    except ValueError:
        return [f"{field} must use YYYY-MM-DD"]
    return []


def validate_use_case_record(
    record: dict[str, Any], vocab: dict[str, Any], mapping: dict[str, Any]
) -> list[str]:
    errors = _missing(
        record,
        ["schema_version", "ai_id", "name", "department", "description", "ownership", "governance", "inventory", "risk", "dates", "record_status"],
    )
    if errors:
        return errors

    if record["schema_version"] != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not AI_ID.fullmatch(str(record["ai_id"])):
        errors.append("ai_id must match AI-####")
    for field in ("name", "department", "description"):
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{field} must be a non-empty string")

    ownership = record["ownership"]
    if not isinstance(ownership, dict):
        errors.append("ownership must be an object")
    else:
        errors.extend(_missing(ownership, ["business_owner", "coe_owner"], "ownership."))

    governance = record["governance"]
    inventory = record["inventory"]
    risk = record["risk"]
    dates = record["dates"]
    if not all(isinstance(value, dict) for value in (governance, inventory, risk, dates)):
        errors.append("governance, inventory, risk, and dates must be objects")
        return errors

    errors.extend(_missing(governance, ["phase", "substage", "gate_status", "priority", "build_buy"], "governance."))
    errors.extend(_missing(inventory, ["bucket", "operational_status"], "inventory."))
    errors.extend(_missing(risk, ["tier", "data_sensitivity", "resident_facing", "public_safety", "human_oversight"], "risk."))
    errors.extend(_missing(dates, ["created", "last_updated"], "dates."))
    if errors:
        return errors

    errors += _enum(governance["phase"], vocab["governance_phases"], "governance.phase")
    errors += _enum(governance["gate_status"], vocab["gate_statuses"], "governance.gate_status")
    errors += _enum(governance["priority"], vocab["priorities"], "governance.priority")
    errors += _enum(governance["build_buy"], vocab["build_buy"], "governance.build_buy")
    errors += _enum(inventory["bucket"], vocab["inventory_buckets"], "inventory.bucket")
    errors += _enum(inventory["operational_status"], vocab["operational_statuses"], "inventory.operational_status")
    errors += _enum(risk["tier"], vocab["risk_tiers"], "risk.tier")
    errors += _enum(risk["data_sensitivity"], vocab["data_sensitivities"], "risk.data_sensitivity")
    errors += _enum(risk["human_oversight"], vocab["human_oversight"], "risk.human_oversight")
    errors += _enum(record["record_status"], vocab["record_statuses"], "record_status")

    phase_map = {item["governance_phase"]: item for item in mapping["phases"]}
    phase = phase_map.get(governance["phase"])
    if phase:
        if inventory["bucket"] not in phase["allowed_inventory_buckets"]:
            errors.append(
                f"inventory.bucket {inventory['bucket']!r} is not allowed for governance.phase {governance['phase']!r}"
            )
        if governance["substage"] not in phase["allowed_substages"]:
            errors.append(
                f"governance.substage {governance['substage']!r} is not allowed for governance.phase {governance['phase']!r}"
            )

    for flag in ("resident_facing", "public_safety"):
        if not isinstance(risk[flag], bool):
            errors.append(f"risk.{flag} must be true or false")

    for field in ("created", "last_updated", "target_production", "go_live", "closed"):
        if field in dates:
            errors += _date(dates[field], f"dates.{field}")
    if governance.get("next_gate_date") is not None:
        errors += _date(governance["next_gate_date"], "governance.next_gate_date")

    if inventory["bucket"] == "priority_backlog" and not inventory.get("backlog_reason"):
        errors.append("priority_backlog records require inventory.backlog_reason")
    if inventory["bucket"] == "in_production":
        monitoring = record.get("monitoring")
        if not isinstance(monitoring, dict) or not monitoring.get("owner") or not monitoring.get("cadence"):
            errors.append("in_production records require monitoring.owner and monitoring.cadence")
        if not dates.get("go_live"):
            errors.append("in_production records require dates.go_live")
    if inventory["bucket"] in {"resolved", "decommissioned"}:
        if not dates.get("closed"):
            errors.append("closed inventory records require dates.closed")
        if not inventory.get("resolution"):
            errors.append("closed inventory records require inventory.resolution")

    licenses = record.get("licenses", [])
    if not isinstance(licenses, list):
        errors.append("licenses must be an array")
    else:
        for index, item in enumerate(licenses):
            if not isinstance(item, dict):
                errors.append(f"licenses[{index}] must be an object")
                continue
            errors.extend(_missing(item, ["license_id", "quantity", "status"], f"licenses[{index}]."))
            if "license_id" in item and not LICENSE_ID.fullmatch(str(item["license_id"])):
                errors.append(f"licenses[{index}].license_id must match LIC-####")
            if "quantity" in item and (not isinstance(item["quantity"], int) or item["quantity"] < 0):
                errors.append(f"licenses[{index}].quantity must be a non-negative integer")
            if "status" in item:
                errors += _enum(item["status"], vocab["license_statuses"], f"licenses[{index}].status")
    return errors


def validate_license_record(record: dict[str, Any], vocab: dict[str, Any]) -> list[str]:
    errors = _missing(record, ["schema_version", "license_id", "tool_name", "vendor", "capacity", "status", "last_updated"])
    if errors:
        return errors
    if record["schema_version"] != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not LICENSE_ID.fullmatch(str(record["license_id"])):
        errors.append("license_id must match LIC-####")
    capacity = record["capacity"]
    if not isinstance(capacity, dict):
        errors.append("capacity must be an object")
    else:
        errors += _missing(capacity, ["purchased", "assigned", "available"], "capacity.")
        if not errors:
            for field in ("purchased", "assigned", "available"):
                if not isinstance(capacity[field], int) or capacity[field] < 0:
                    errors.append(f"capacity.{field} must be a non-negative integer")
            if all(isinstance(capacity.get(field), int) for field in ("purchased", "assigned", "available")):
                if capacity["purchased"] != capacity["assigned"] + capacity["available"]:
                    errors.append("capacity.purchased must equal capacity.assigned + capacity.available")
    errors += _enum(record["status"], vocab["record_statuses"], "status")
    errors += _date(record["last_updated"], "last_updated", nullable=False)
    if record.get("renewal_date") is not None:
        errors += _date(record["renewal_date"], "renewal_date")
    return errors


def validate_issue_record(record: dict[str, Any], vocab: dict[str, Any]) -> list[str]:
    errors = _missing(record, ["schema_version", "issue_id", "ai_id", "summary", "issue_type", "severity", "status", "owner", "date_opened", "last_updated"])
    if errors:
        return errors
    if record["schema_version"] != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not ISSUE_ID.fullmatch(str(record["issue_id"])):
        errors.append("issue_id must match ISS-####")
    if not AI_ID.fullmatch(str(record["ai_id"])):
        errors.append("ai_id must match AI-####")
    errors += _enum(record["severity"], vocab["issue_severities"], "severity")
    errors += _enum(record["status"], vocab["issue_statuses"], "status")
    errors += _date(record["date_opened"], "date_opened", nullable=False)
    errors += _date(record["last_updated"], "last_updated", nullable=False)
    if record.get("date_closed") is not None:
        errors += _date(record["date_closed"], "date_closed")
    if record["status"] in {"resolved", "closed"}:
        if not record.get("date_closed"):
            errors.append("resolved or closed issues require date_closed")
        if not record.get("resolution"):
            errors.append("resolved or closed issues require resolution")
    return errors


def validate_cross_references(
    use_cases: list[dict[str, Any]], licenses: list[dict[str, Any]], issues: list[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    use_case_ids = {record["ai_id"] for record in use_cases if "ai_id" in record}
    license_ids = {record["license_id"] for record in licenses if "license_id" in record}

    for issue in issues:
        if issue.get("ai_id") not in use_case_ids:
            errors.append(f"{issue.get('issue_id', '<unknown>')} references missing use case {issue.get('ai_id')}")
    for use_case in use_cases:
        for license_ref in use_case.get("licenses", []):
            if license_ref.get("license_id") not in license_ids:
                errors.append(f"{use_case.get('ai_id')} references missing license {license_ref.get('license_id')}")
    for license_record in licenses:
        for ai_id in license_record.get("supported_use_cases", []):
            if ai_id not in use_case_ids:
                errors.append(f"{license_record.get('license_id')} references missing use case {ai_id}")
    return errors


def duplicate_ids(records: list[dict[str, Any]], field: str) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        value = record.get(field)
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)
