#!/usr/bin/env python3
"""Validate public AI use cases and emit an allowlisted leadership dataset."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USE_CASES = ROOT / "use-cases"
CATALOG_PATH = ROOT / "governance" / "controls.json"
OUTPUT = ROOT / "data" / "use-cases.json"

PHASES = ["Intake", "Qualify", "Prioritize", "Design", "Develop", "Test", "Deploy", "Monitor", "Close"]
PHASE_FOLDERS = {
    "Intake": "01 Intake", "Qualify": "02 Qualify", "Prioritize": "03 Prioritize",
    "Design": "04 Design", "Develop": "05 Develop", "Test": "06 Test",
    "Deploy": "07 Deploy", "Monitor": "08 Monitor", "Close": "09 Close",
}
STATUSES = {"In Progress", "Backlog", "Live", "On Hold", "Closed"}
HEALTH_STATUSES = {"On Track", "At Risk", "Blocked", "Needs Review"}
RISK_TIERS = {"Not Assessed", "Low", "Moderate", "High", "Critical"}
REVIEW_STATUSES = {"Not Started", "In Review", "Approved", "Approved with Conditions", "Changes Needed", "Not Required"}
REVIEW_GROUPS = {"Cyber", "Data", "Application", "Network", "Enterprise"}
REVIEW_APPLICABILITY = {"Required", "Not Required"}
PHASE_STATUSES = {"Not Started", "In Progress", "Complete", "Blocked", "Not Applicable"}
REQUIREMENT_STATUSES = PHASE_STATUSES
GATE_STATUSES = {"Not Started", "In Review", "Changes Needed", "Ready", "Approved", "Approved with Conditions", "Not Required"}
SEVERITIES = {"Critical", "High", "Medium", "Low"}
ISSUE_STATUSES = {"Open", "Monitoring", "Resolved"}
RISK_STATUSES = {"Open", "Mitigating", "Monitoring", "Accepted", "Closed"}
RISK_RATINGS = {"Not Assessed", "Low", "Moderate", "High", "Critical"}
MONITORING_RESULTS = {"Not Started", "On Track", "At Risk", "Action Required", "Not Applicable"}
METRIC_STATUSES = {"Not Started", "On Track", "At Risk", "Breached", "Not Applicable"}
CLOSURE_REASONS = {None, "Completed", "Rejected", "Withdrawn", "Decommissioned"}


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: cannot read valid JSON ({exc})")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path}: root value must be an object")
        return {}
    return value


def parse_iso_date(value: object, field: str, errors: list[str], source: Path) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"{source}: {field} must use YYYY-MM-DD")
        return None


def validate_evidence(values: object, field: str, errors: list[str], source: Path) -> None:
    if not isinstance(values, list):
        errors.append(f"{source}: {field} must be a list")
        return
    for position, value in enumerate(values, start=1):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{source}: {field} item {position} must be a non-empty public-safe label or path")


def validate_catalog(catalog: dict, errors: list[str]) -> None:
    phases = catalog.get("phases")
    if not isinstance(phases, list):
        errors.append(f"{CATALOG_PATH}: phases must be a list")
        return
    names = [item.get("name") for item in phases if isinstance(item, dict)]
    if names != PHASES:
        errors.append(f"{CATALOG_PATH}: phases must appear once in lifecycle order: {', '.join(PHASES)}")
    control_ids: set[str] = set()
    for phase in phases:
        if not isinstance(phase, dict):
            errors.append(f"{CATALOG_PATH}: every phase must be an object")
            continue
        if not phase.get("playbookPhase"):
            errors.append(f"{CATALOG_PATH}: {phase.get('name')} missing playbookPhase")
        controls = phase.get("controls")
        if not isinstance(controls, list) or not controls:
            errors.append(f"{CATALOG_PATH}: {phase.get('name')} requires controls")
            continue
        for control in controls:
            if not isinstance(control, dict):
                errors.append(f"{CATALOG_PATH}: {phase.get('name')} control must be an object")
                continue
            for field in ("id", "title", "required", "reviewGroups"):
                if field not in control:
                    errors.append(f"{CATALOG_PATH}: {phase.get('name')} control missing '{field}'")
            control_id = control.get("id")
            if control_id in control_ids:
                errors.append(f"{CATALOG_PATH}: duplicate control ID '{control_id}'")
            control_ids.add(control_id)
            unknown_groups = set(control.get("reviewGroups", [])) - REVIEW_GROUPS
            if unknown_groups:
                errors.append(f"{CATALOG_PATH}: {control_id} has unsupported review groups {', '.join(sorted(unknown_groups))}")
    if set(catalog.get("reviewGroups", [])) != REVIEW_GROUPS:
        errors.append(f"{CATALOG_PATH}: reviewGroups must contain Cyber, Data, Application, Network, and Enterprise")


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


def validate_checklists(folder: Path, catalog: dict, errors: list[str]) -> None:
    for phase in catalog.get("phases", []):
        name = phase.get("name")
        checklist = folder / PHASE_FOLDERS.get(name, "") / "CHECKLIST.md"
        if not checklist.exists():
            errors.append(f"{folder}: missing checklist for {name}")
            continue
        text = checklist.read_text(encoding="utf-8")
        actual = re.findall(r"`([A-Z]{3}-\d{2})`", text)
        expected = [control.get("id") for control in phase.get("controls", [])]
        if actual != expected:
            errors.append(f"{checklist}: control IDs must match controls.json in order ({', '.join(expected)})")


def validate_status(record: dict, source: Path, errors: list[str]) -> None:
    for required in (
        "id", "name", "department", "owner", "sponsor", "phase", "status", "health",
        "riskTier", "currentStep", "currentActivity", "lastUpdated",
    ):
        if not record.get(required):
            errors.append(f"{source}: missing required field '{required}'")
    if record.get("schemaVersion") != 2:
        errors.append(f"{source}: schemaVersion must be 2")
    if record.get("phase") not in PHASES:
        errors.append(f"{source}: unknown governance phase '{record.get('phase')}'")
    if record.get("status") not in STATUSES:
        errors.append(f"{source}: unknown status '{record.get('status')}'")
    if record.get("health") not in HEALTH_STATUSES:
        errors.append(f"{source}: unsupported health '{record.get('health')}'")
    if record.get("riskTier") not in RISK_TIERS:
        errors.append(f"{source}: unsupported riskTier '{record.get('riskTier')}'")
    if record.get("reviewStatus") not in REVIEW_STATUSES:
        errors.append(f"{source}: unsupported reviewStatus '{record.get('reviewStatus')}'")
    if record.get("closureReason") not in CLOSURE_REASONS:
        errors.append(f"{source}: unsupported closureReason '{record.get('closureReason')}'")
    if record.get("status") == "Closed" and not record.get("closureReason"):
        errors.append(f"{source}: Closed records require a closureReason")
    for field in ("lastUpdated", "phaseEnteredDate", "targetPhaseExitDate", "nextDecisionDate"):
        parse_iso_date(record.get(field), field, errors, source)
    benefits = record.get("benefits")
    if not isinstance(benefits, dict):
        errors.append(f"{source}: benefits must be an object")
    else:
        for required in ("measure", "baseline", "target", "current", "cadence"):
            if not benefits.get(required):
                errors.append(f"{source}: benefits missing '{required}'")
    issues = record.get("issues", [])
    if not isinstance(issues, list):
        errors.append(f"{source}: issues must be a list")
        return
    for position, issue in enumerate(issues, start=1):
        prefix = f"issue {position}"
        if not isinstance(issue, dict):
            errors.append(f"{source}: {prefix} must be an object")
            continue
        for required in ("id", "title", "severity", "status", "owner"):
            if not issue.get(required):
                errors.append(f"{source}: {prefix} missing '{required}'")
        if issue.get("severity") not in SEVERITIES:
            errors.append(f"{source}: {prefix} has unsupported severity '{issue.get('severity')}'")
        if issue.get("status") not in ISSUE_STATUSES:
            errors.append(f"{source}: {prefix} has unsupported status '{issue.get('status')}'")
        parse_iso_date(issue.get("targetDate"), f"{prefix} targetDate", errors, source)
        parse_iso_date(issue.get("resolvedDate"), f"{prefix} resolvedDate", errors, source)


def validate_governance(governance: dict, source: Path, catalog: dict, errors: list[str]) -> None:
    if governance.get("schemaVersion") != 1:
        errors.append(f"{source}: schemaVersion must be 1")
    catalog_phases = {item["name"]: item for item in catalog.get("phases", [])}
    all_control_ids = {control["id"] for phase in catalog.get("phases", []) for control in phase.get("controls", [])}
    progress = governance.get("phaseProgress")
    if not isinstance(progress, list):
        errors.append(f"{source}: phaseProgress must be a list")
        progress = []
    seen_phases: set[str] = set()
    for position, phase in enumerate(progress, start=1):
        prefix = f"phaseProgress item {position}"
        if not isinstance(phase, dict):
            errors.append(f"{source}: {prefix} must be an object")
            continue
        name = phase.get("phase")
        if name not in catalog_phases:
            errors.append(f"{source}: {prefix} has unknown phase '{name}'")
            continue
        if name in seen_phases:
            errors.append(f"{source}: duplicate phaseProgress entry '{name}'")
        seen_phases.add(name)
        if phase.get("status") not in PHASE_STATUSES:
            errors.append(f"{source}: {name} has unsupported phase status '{phase.get('status')}'")
        for field in ("startedDate", "targetDate", "completedDate"):
            parse_iso_date(phase.get(field), f"{name} {field}", errors, source)
        if phase.get("status") == "Complete" and not phase.get("completedDate"):
            errors.append(f"{source}: completed {name} phase requires completedDate")
        gate = phase.get("gate")
        if not isinstance(gate, dict):
            errors.append(f"{source}: {name} gate must be an object")
        else:
            if gate.get("status") not in GATE_STATUSES:
                errors.append(f"{source}: {name} has unsupported gate status '{gate.get('status')}'")
            if gate.get("decisionByGroup") and gate.get("decisionByGroup") not in REVIEW_GROUPS:
                errors.append(f"{source}: {name} gate has unsupported decisionByGroup '{gate.get('decisionByGroup')}'")
            for field in ("decisionDate", "exceptionExpirationDate"):
                parse_iso_date(gate.get(field), f"{name} gate {field}", errors, source)
            if gate.get("status") in {"Approved", "Approved with Conditions"} and not gate.get("decisionDate"):
                errors.append(f"{source}: {name} approved gate requires decisionDate")
            if gate.get("status") in {"Approved", "Approved with Conditions"} and not gate.get("decision"):
                errors.append(f"{source}: {name} approved gate requires decision")
            if gate.get("status") in {"Approved", "Approved with Conditions"} and not gate.get("decisionByGroup"):
                errors.append(f"{source}: {name} approved gate requires decisionByGroup")
            if gate.get("status") == "Approved with Conditions" and not gate.get("conditions"):
                errors.append(f"{source}: {name} approved-with-conditions gate requires conditions")
        requirements = phase.get("requirements")
        if not isinstance(requirements, dict):
            errors.append(f"{source}: {name} requirements must be an object keyed by control ID")
            continue
        known = {control["id"] for control in catalog_phases[name].get("controls", [])}
        for control_id, value in requirements.items():
            if control_id not in known:
                errors.append(f"{source}: {name} references unknown control '{control_id}'")
                continue
            if not isinstance(value, dict):
                errors.append(f"{source}: {name} control {control_id} must be an object")
                continue
            if value.get("status") not in REQUIREMENT_STATUSES:
                errors.append(f"{source}: {name} control {control_id} has unsupported status '{value.get('status')}'")
            if value.get("ownerGroup") and value.get("ownerGroup") not in REVIEW_GROUPS:
                errors.append(f"{source}: {name} control {control_id} has unsupported ownerGroup '{value.get('ownerGroup')}'")
            for field in ("targetDate", "completedDate"):
                parse_iso_date(value.get(field), f"{name} {control_id} {field}", errors, source)
            validate_evidence(value.get("evidence", []), f"{name} {control_id} evidence", errors, source)
            if value.get("status") == "Complete" and not value.get("completedDate"):
                errors.append(f"{source}: completed {name} control {control_id} requires completedDate")
            if value.get("status") == "Complete" and not value.get("evidence"):
                errors.append(f"{source}: completed {name} control {control_id} requires public-safe evidence or 'Reviewed internally'")
            if value.get("status") == "Not Applicable" and not value.get("notes"):
                errors.append(f"{source}: not-applicable {name} control {control_id} requires rationale in notes")
    missing_phases = set(PHASES) - seen_phases
    if missing_phases:
        errors.append(f"{source}: phaseProgress missing {', '.join(sorted(missing_phases))}")

    reviews = governance.get("formalReviews")
    if not isinstance(reviews, list):
        errors.append(f"{source}: formalReviews must be a list")
        reviews = []
    seen_groups: set[str] = set()
    for position, review in enumerate(reviews, start=1):
        prefix = f"formal review {position}"
        if not isinstance(review, dict):
            errors.append(f"{source}: {prefix} must be an object")
            continue
        group = review.get("group")
        if group not in REVIEW_GROUPS:
            errors.append(f"{source}: {prefix} has unsupported group '{group}'")
        elif group in seen_groups:
            errors.append(f"{source}: duplicate formal review group '{group}'")
        seen_groups.add(group)
        if review.get("phase") not in PHASES:
            errors.append(f"{source}: {prefix} has unknown phase '{review.get('phase')}'")
        if review.get("applicability") not in REVIEW_APPLICABILITY:
            errors.append(f"{source}: {prefix} has unsupported applicability '{review.get('applicability')}'")
        if review.get("status") not in REVIEW_STATUSES:
            errors.append(f"{source}: {prefix} has unsupported status '{review.get('status')}'")
        for field in ("submittedDate", "decisionDate"):
            parse_iso_date(review.get(field), f"{prefix} {field}", errors, source)
        validate_evidence(review.get("evidence", []), f"{prefix} evidence", errors, source)
        if review.get("status") in {"Approved", "Approved with Conditions"} and not review.get("decisionDate"):
            errors.append(f"{source}: approved {group} review requires decisionDate")
        if review.get("status") == "Approved with Conditions" and not review.get("conditions"):
            errors.append(f"{source}: {group} review approved with conditions requires conditions")
        if review.get("applicability") == "Required" and review.get("status") == "Not Required":
            errors.append(f"{source}: required {group} review cannot have status Not Required")
        if review.get("applicability") == "Not Required" and review.get("status") != "Not Required":
            errors.append(f"{source}: non-applicable {group} review must have status Not Required")
        if review.get("status") in {"Approved", "Approved with Conditions"} and not review.get("evidence"):
            errors.append(f"{source}: approved {group} review requires public-safe evidence or 'Reviewed internally'")
    missing_groups = REVIEW_GROUPS - seen_groups
    if missing_groups:
        errors.append(f"{source}: formalReviews missing {', '.join(sorted(missing_groups))}")

    risks = governance.get("technicalRisks")
    if not isinstance(risks, list):
        errors.append(f"{source}: technicalRisks must be a list")
        risks = []
    seen_risks: set[str] = set()
    for position, risk in enumerate(risks, start=1):
        prefix = f"technical risk {position}"
        if not isinstance(risk, dict):
            errors.append(f"{source}: {prefix} must be an object")
            continue
        for required in ("id", "title", "category", "scenario", "ownerGroup", "status", "inherentRisk", "residualRisk", "controls", "mitigation"):
            if not risk.get(required):
                errors.append(f"{source}: {prefix} missing '{required}'")
        risk_id = risk.get("id")
        if risk_id in seen_risks:
            errors.append(f"{source}: duplicate technical risk ID '{risk_id}'")
        seen_risks.add(risk_id)
        if risk.get("ownerGroup") not in REVIEW_GROUPS:
            errors.append(f"{source}: {prefix} has unsupported ownerGroup '{risk.get('ownerGroup')}'")
        if risk.get("status") not in RISK_STATUSES:
            errors.append(f"{source}: {prefix} has unsupported status '{risk.get('status')}'")
        for field in ("inherentRisk", "residualRisk"):
            if risk.get(field) not in RISK_RATINGS:
                errors.append(f"{source}: {prefix} has unsupported {field} '{risk.get(field)}'")
        for field in ("targetDate", "decisionDate", "exceptionExpirationDate"):
            parse_iso_date(risk.get(field), f"{prefix} {field}", errors, source)
        validate_evidence(risk.get("evidence", []), f"{prefix} evidence", errors, source)
        if not isinstance(risk.get("controls"), list):
            errors.append(f"{source}: {prefix} controls must be a list of governance control IDs")
        else:
            unknown_controls = set(risk.get("controls", [])) - all_control_ids
            if unknown_controls:
                errors.append(f"{source}: {prefix} references unknown controls {', '.join(sorted(unknown_controls))}")
        if risk.get("residualRisk") in {"High", "Critical"} and risk.get("status") == "Accepted" and not risk.get("decisionDate"):
            errors.append(f"{source}: accepted high/critical {prefix} requires decisionDate")

    decisions = governance.get("decisions")
    if not isinstance(decisions, list):
        errors.append(f"{source}: decisions must be a list")
        decisions = []
    for position, decision in enumerate(decisions, start=1):
        prefix = f"decision {position}"
        if not isinstance(decision, dict):
            errors.append(f"{source}: {prefix} must be an object")
            continue
        for required in ("id", "phase", "type", "decision", "outcome", "decisionDate", "decisionByGroup"):
            if not decision.get(required):
                errors.append(f"{source}: {prefix} missing '{required}'")
        if decision.get("phase") not in PHASES:
            errors.append(f"{source}: {prefix} has unknown phase '{decision.get('phase')}'")
        if decision.get("decisionByGroup") not in REVIEW_GROUPS:
            errors.append(f"{source}: {prefix} has unsupported decisionByGroup '{decision.get('decisionByGroup')}'")
        parse_iso_date(decision.get("decisionDate"), f"{prefix} decisionDate", errors, source)

    monitoring = governance.get("monitoring")
    if not isinstance(monitoring, dict):
        errors.append(f"{source}: monitoring must be an object")
    else:
        if not monitoring.get("cadence"):
            errors.append(f"{source}: monitoring cadence is required")
        if monitoring.get("overallResult") not in MONITORING_RESULTS:
            errors.append(f"{source}: unsupported monitoring overallResult '{monitoring.get('overallResult')}'")
        for field in ("lastReviewDate", "nextReviewDate"):
            parse_iso_date(monitoring.get(field), f"monitoring {field}", errors, source)
        metrics = monitoring.get("metrics")
        if not isinstance(metrics, list):
            errors.append(f"{source}: monitoring metrics must be a list")
        else:
            for position, metric in enumerate(metrics, start=1):
                prefix = f"monitoring metric {position}"
                if not isinstance(metric, dict):
                    errors.append(f"{source}: {prefix} must be an object")
                    continue
                for required in ("id", "name", "ownerGroup", "target", "current", "status"):
                    if not metric.get(required):
                        errors.append(f"{source}: {prefix} missing '{required}'")
                if metric.get("ownerGroup") not in REVIEW_GROUPS:
                    errors.append(f"{source}: {prefix} has unsupported ownerGroup '{metric.get('ownerGroup')}'")
                if metric.get("status") not in METRIC_STATUSES:
                    errors.append(f"{source}: {prefix} has unsupported status '{metric.get('status')}'")
                parse_iso_date(metric.get("lastMeasuredDate"), f"{prefix} lastMeasuredDate", errors, source)
                validate_evidence(metric.get("evidence", []), f"{prefix} evidence", errors, source)


def enrich_phases(governance: dict, catalog: dict) -> list[dict]:
    progress_by_name = {item.get("phase"): item for item in governance.get("phaseProgress", []) if isinstance(item, dict)}
    result: list[dict] = []
    for catalog_phase in catalog.get("phases", []):
        name = catalog_phase["name"]
        progress = progress_by_name.get(name, {})
        overrides = progress.get("requirements", {}) if isinstance(progress.get("requirements"), dict) else {}
        requirements = []
        for control in catalog_phase.get("controls", []):
            override = overrides.get(control["id"], {}) if isinstance(overrides.get(control["id"], {}), dict) else {}
            requirements.append({
                "id": control["id"],
                "title": control["title"],
                "required": bool(control.get("required")),
                "reviewGroups": control.get("reviewGroups", []),
                "status": override.get("status", "Not Started"),
                "ownerGroup": override.get("ownerGroup"),
                "targetDate": override.get("targetDate"),
                "completedDate": override.get("completedDate"),
                "evidence": override.get("evidence", []),
                "notes": override.get("notes", ""),
            })
        required_items = [item for item in requirements if item["required"]]
        done = sum(item["status"] in {"Complete", "Not Applicable"} for item in required_items)
        result.append({
            "phase": name,
            "playbookPhase": catalog_phase.get("playbookPhase"),
            "status": progress.get("status", "Not Started"),
            "startedDate": progress.get("startedDate"),
            "targetDate": progress.get("targetDate"),
            "completedDate": progress.get("completedDate"),
            "gate": progress.get("gate", {}),
            "requirements": requirements,
            "done": done,
            "total": len(required_items),
            "readiness": round(done / len(required_items) * 100) if required_items else 0,
        })
    return result


def export() -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    catalog = read_json(CATALOG_PATH, errors)
    validate_catalog(catalog, errors)
    validate_checklists(USE_CASES / "_template", catalog, errors)
    published: list[dict] = []
    seen_ids: set[str] = set()
    for source in sorted(USE_CASES.glob("*/status.json")):
        if source.parent.name.startswith("_"):
            continue
        validate_checklists(source.parent, catalog, errors)
        record = read_json(source, errors)
        if not record:
            continue
        validate_status(record, source, errors)
        governance_source = source.parent / "governance.json"
        governance = read_json(governance_source, errors)
        if governance:
            validate_governance(governance, governance_source, catalog, errors)
        record_id = record.get("id")
        if record_id in seen_ids:
            errors.append(f"{source}: duplicate use-case ID '{record_id}'")
        seen_ids.add(record_id)
        if not record.get("publish"):
            continue
        phases = enrich_phases(governance, catalog)
        current = next((phase for phase in phases if phase["phase"] == record.get("phase")), None) or {}
        reviews = governance.get("formalReviews", [])
        risks = governance.get("technicalRisks", [])
        published.append({
            "schemaVersion": 2,
            "folderPath": f"AI Inventory/use-cases/{source.parent.name}",
            "id": record.get("id"),
            "name": record.get("name"),
            "department": record.get("department"),
            "owner": record.get("owner"),
            "sponsor": record.get("sponsor"),
            "phase": record.get("phase"),
            "status": record.get("status"),
            "health": record.get("health"),
            "riskTier": record.get("riskTier"),
            "reviewStatus": record.get("reviewStatus"),
            "currentStep": record.get("currentStep"),
            "currentActivity": record.get("currentActivity"),
            "blocker": record.get("blocker"),
            "phaseEnteredDate": record.get("phaseEnteredDate"),
            "targetPhaseExitDate": record.get("targetPhaseExitDate"),
            "nextDecision": record.get("nextDecision"),
            "nextDecisionDate": record.get("nextDecisionDate"),
            "lastUpdated": record.get("lastUpdated"),
            "summary": record.get("summary"),
            "benefits": record.get("benefits"),
            "closureReason": record.get("closureReason"),
            "checklist": {"done": current.get("done", 0), "total": current.get("total", 0)},
            "checklistDone": current.get("done", 0),
            "checklistTotal": current.get("total", 0),
            "gateReadiness": current.get("readiness", 0),
            "phases": phases,
            "formalReviews": reviews,
            "technicalRisks": risks,
            "decisions": governance.get("decisions", []),
            "monitoring": governance.get("monitoring", {}),
            "issues": [public_issue(issue) for issue in record.get("issues", []) if issue.get("publish", True)],
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
    payload = {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "AI CoE public governance workspace",
        "useCases": sorted(use_cases, key=lambda item: item["id"] or ""),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Published {len(use_cases)} public-safe use case(s) to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
