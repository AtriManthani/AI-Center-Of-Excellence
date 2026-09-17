"""Generate a deterministic Markdown dashboard from approved inventory records."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from repository_model import ISSUE_DIR, LICENSE_DIR, ROOT, USE_CASE_DIR, load_configuration, load_records


OUTPUT_PATH = ROOT / "inventory" / "dashboard" / "AI-INVENTORY.md"


def cell(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: list[list[Any]], empty_message: str) -> list[str]:
    if not rows:
        return [f"_{empty_message}_", ""]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    lines.append("")
    return lines


def render() -> str:
    _, mapping = load_configuration()
    phase_names = {item["governance_phase"]: item["display_name"] for item in mapping["phases"]}
    use_cases = [record for _, record in load_records(USE_CASE_DIR)]
    licenses = [record for _, record in load_records(LICENSE_DIR)]
    issues = [record for _, record in load_records(ISSUE_DIR)]
    use_cases.sort(key=lambda item: item["ai_id"])
    licenses.sort(key=lambda item: item["license_id"])
    issues.sort(key=lambda item: item["issue_id"])

    buckets = Counter(record["inventory"]["bucket"] for record in use_cases)
    open_issues = [record for record in issues if record["status"] not in {"resolved", "closed"}]
    purchased = sum(record["capacity"]["purchased"] for record in licenses)
    assigned = sum(record["capacity"]["assigned"] for record in licenses)
    available = sum(record["capacity"]["available"] for record in licenses)
    utilization = (assigned / purchased * 100) if purchased else 0.0

    lines = [
        "# AI Inventory Dashboard",
        "",
        "> Generated from approved records in `inventory/data/`. Do not edit calculated sections manually.",
        "",
        "## Portfolio summary",
        "",
        "| Measure | Count |",
        "| --- | ---: |",
        f"| Total use cases | {len(use_cases)} |",
        f"| Pre-inventory | {buckets['pre_inventory']} |",
        f"| Prioritization | {buckets['prioritization']} |",
        f"| In progress | {buckets['in_progress']} |",
        f"| Priority backlog | {buckets['priority_backlog']} |",
        f"| In production | {buckets['in_production']} |",
        f"| Resolved | {buckets['resolved']} |",
        f"| Decommissioned | {buckets['decommissioned']} |",
        f"| Open issues | {len(open_issues)} |",
        "",
        "## License summary",
        "",
        "| Measure | Count |",
        "| --- | ---: |",
        f"| Purchased | {purchased} |",
        f"| Assigned | {assigned} |",
        f"| Available | {available} |",
        f"| Utilization | {utilization:.1f}% |",
        "",
        "## Active use cases",
        "",
    ]

    active = [record for record in use_cases if record["inventory"]["bucket"] in {"prioritization", "in_progress"}]
    lines += table(
        ["AI ID", "Use case", "Department", "Phase", "Substage", "Status", "Priority", "Risk"],
        [[record["ai_id"], record["name"], record["department"], phase_names.get(record["governance"]["phase"], record["governance"]["phase"]), record["governance"]["substage"], record["inventory"]["operational_status"], record["governance"]["priority"], record["risk"]["tier"]] for record in active],
        "No approved active use-case records have been added.",
    )
    lines += ["## Priority backlog", ""]
    backlog = [record for record in use_cases if record["inventory"]["bucket"] == "priority_backlog"]
    lines += table(
        ["AI ID", "Use case", "Department", "Priority", "Reason"],
        [[record["ai_id"], record["name"], record["department"], record["governance"]["priority"], record["inventory"].get("backlog_reason")] for record in backlog],
        "No approved backlog records have been added.",
    )
    lines += ["## Production and monitoring", ""]
    production = [record for record in use_cases if record["inventory"]["bucket"] == "in_production"]
    lines += table(
        ["AI ID", "Use case", "Department", "Go-live", "Status", "Monitoring owner", "Cadence"],
        [[record["ai_id"], record["name"], record["department"], record["dates"].get("go_live"), record["inventory"]["operational_status"], (record.get("monitoring") or {}).get("owner"), (record.get("monitoring") or {}).get("cadence")] for record in production],
        "No approved production records have been added.",
    )
    lines += ["## Open issues", ""]
    lines += table(
        ["Issue ID", "AI ID", "Summary", "Severity", "Status", "Owner", "Opened"],
        [[record["issue_id"], record["ai_id"], record["summary"], record["severity"], record["status"], record["owner"], record["date_opened"]] for record in open_issues],
        "No open issues have been added.",
    )
    lines += ["## License capacity", ""]
    lines += table(
        ["License ID", "Tool", "Purchased", "Assigned", "Available", "Utilization"],
        [[record["license_id"], record["tool_name"], record["capacity"]["purchased"], record["capacity"]["assigned"], record["capacity"]["available"], f"{(record['capacity']['assigned'] / record['capacity']['purchased'] * 100) if record['capacity']['purchased'] else 0.0:.1f}%"] for record in licenses],
        "No approved license records have been added.",
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the committed dashboard is stale")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != rendered:
            print("Dashboard is stale. Run: python tools/generate_dashboard.py")
            return 1
        print("Dashboard is current.")
        return 0
    OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Generated {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
