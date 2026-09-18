#!/usr/bin/env python3
"""Validate public AI use cases and emit an allowlisted leadership dataset."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USE_CASES = ROOT / "use-cases"
OUTPUT = ROOT / "dist" / "use-cases.json"

PHASES = {
    "Opportunity Identification",
    "Opportunity Qualification",
    "Opportunity Prioritization",
    "Solution Design",
    "Solution Development",
    "Solution Testing",
    "Solution Deployment",
    "Solution Monitoring & Improvement",
    "Solution Closeout",
}
STATUSES = {"In Progress", "Backlog", "Live", "On Hold", "Closed"}
HEALTH = {"Green", "Amber", "Red"}
SEVERITIES = {"Critical", "High", "Medium", "Low"}
ISSUE_STATUSES = {"Open", "Monitoring", "Resolved"}
CLOSURE_REASONS = {None, "Completed", "Rejected", "Withdrawn", "Decommissioned"}


def parse_iso_date(value: object, field: str, errors: list[str], source: Path) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"{source}: {field} must use YYYY-MM-DD")
        return None


def calculate_health(record: dict, today: date) -> str:
    override = record.get("healthOverride")
    if override in HEALTH:
        return override
    open_issues = [issue for issue in record.get("issues", []) if issue.get("status") != "Resolved"]
    if any(issue.get("severity") in {"Critical", "High"} for issue in open_issues):
        return "Red"
    if record.get("blocker") or record.get("status") == "On Hold":
        return "Amber"
    target = record.get("nextDecisionDate")
    if target:
        try:
            if date.fromisoformat(target) < today and record.get("status") in {"In Progress", "Live"}:
                return "Amber"
        except ValueError:
            pass
    return "Green"


def public_issue(issue: dict) -> dict:
    return {
        "id": issue.get("id"),
        "title": issue.get("title"),
        "severity": issue.get("severity"),
        "status": issue.get("status"),
        "owner": issue.get("owner"),
        "targetDate": issue.get("targetDate"),
        "resolvedDate": issue.get("resolvedDate"),
        "mitigationSummary": issue.get("mitigationSummary"),
    }


def validate_record(record: dict, source: Path, errors: list[str]) -> None:
    for required in ("id", "name", "department", "owner", "phase", "status", "currentActivity", "lastUpdated"):
        if not record.get(required):
            errors.append(f"{source}: missing required field '{required}'")
    if record.get("phase") not in PHASES:
        errors.append(f"{source}: unknown governance phase '{record.get('phase')}'")
    if record.get("status") not in STATUSES:
        errors.append(f"{source}: unknown status '{record.get('status')}'")
    if record.get("healthOverride") not in HEALTH | {None, ""}:
        errors.append(f"{source}: healthOverride must be Green, Amber, Red, or null")
    if record.get("healthOverride") and not record.get("healthOverrideReason"):
        errors.append(f"{source}: healthOverrideReason is required when healthOverride is set")
    readiness = record.get("gateReadiness")
    if not isinstance(readiness, (int, float)) or not 0 <= readiness <= 100:
        errors.append(f"{source}: gateReadiness must be a number from 0 to 100")
    if record.get("closureReason") not in CLOSURE_REASONS:
        errors.append(f"{source}: unsupported closureReason '{record.get('closureReason')}'")
    if record.get("status") == "Closed" and not record.get("closureReason"):
        errors.append(f"{source}: Closed records require a closureReason")
    parse_iso_date(record.get("lastUpdated"), "lastUpdated", errors, source)
    parse_iso_date(record.get("nextDecisionDate"), "nextDecisionDate", errors, source)
    for position, issue in enumerate(record.get("issues", []), start=1):
        prefix = f"issue {position}"
        for required in ("id", "title", "severity", "status", "owner"):
            if not issue.get(required):
                errors.append(f"{source}: {prefix} missing '{required}'")
        if issue.get("severity") not in SEVERITIES:
            errors.append(f"{source}: {prefix} has unsupported severity '{issue.get('severity')}'")
        if issue.get("status") not in ISSUE_STATUSES:
            errors.append(f"{source}: {prefix} has unsupported status '{issue.get('status')}'")
        parse_iso_date(issue.get("targetDate"), f"{prefix} targetDate", errors, source)
        parse_iso_date(issue.get("resolvedDate"), f"{prefix} resolvedDate", errors, source)


def export() -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    published: list[dict] = []
    seen_ids: set[str] = set()
    today = date.today()
    for source in sorted(USE_CASES.glob("*/use-case.json")):
        if source.parent.name.startswith("_"):
            continue
        try:
            record = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{source}: cannot read valid JSON ({exc})")
            continue
        validate_record(record, source, errors)
        record_id = record.get("id")
        if record_id in seen_ids:
            errors.append(f"{source}: duplicate use-case ID '{record_id}'")
        seen_ids.add(record_id)
        if not record.get("publish"):
            continue
        published.append({
            "id": record.get("id"),
            "name": record.get("name"),
            "department": record.get("department"),
            "owner": record.get("owner"),
            "phase": record.get("phase"),
            "status": record.get("status"),
            "health": calculate_health(record, today),
            "gateReadiness": record.get("gateReadiness"),
            "currentActivity": record.get("currentActivity"),
            "blocker": record.get("blocker"),
            "nextDecision": record.get("nextDecision"),
            "nextDecisionDate": record.get("nextDecisionDate"),
            "lastUpdated": record.get("lastUpdated"),
            "summary": record.get("summary"),
            "closureReason": record.get("closureReason"),
            "issues": [public_issue(issue) for issue in record.get("issues", []) if issue.get("publish")],
        })
    return published, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="Fail when a public record is invalid")
    args = parser.parse_args()
    use_cases, errors = export()
    if errors:
        print("Inventory validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        if args.validate:
            return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "AI CoE public governance workspace",
        "useCases": sorted(use_cases, key=lambda item: item["id"] or ""),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Published {len(use_cases)} sanitized use case(s) to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

