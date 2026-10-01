# AI Inventory data dictionary

Each use case has two structured records:

- `status.json` contains the current leadership summary.
- `governance.json` contains lifecycle progress, controls, gates, reviews, technical risks, decisions, and monitoring.

Everything committed to the current repository is public. Use group names instead of individual reviewer names, omit sensitive findings, and use an evidence label such as `Reviewed internally` when the supporting artifact cannot be published.

## Requirement status

Requirements are keyed by the stable control IDs in `controls.json`. Only fields that contain use-case-specific progress need to be added.

```json
"DES-09": {
  "status": "In Progress",
  "ownerGroup": "Cyber",
  "targetDate": "2026-10-15",
  "completedDate": null,
  "evidence": ["Reviewed internally"],
  "notes": "Public-safe summary of remaining work."
}
```

Allowed requirement and phase statuses are `Not Started`, `In Progress`, `Complete`, `Blocked`, and `Not Applicable`. A required item marked `Not Applicable` must be supported by an applicable review or gate decision.

## Gate decision

```json
"gate": {
  "status": "Approved with Conditions",
  "decision": "Proceed to development after the recorded conditions are implemented.",
  "decisionDate": "2026-10-20",
  "decisionByGroup": "Enterprise",
  "conditions": "Public-safe statement of the conditions.",
  "exceptionExpirationDate": "2026-12-31"
}
```

Allowed gate statuses are `Not Started`, `In Review`, `Changes Needed`, `Ready`, `Approved`, `Approved with Conditions`, and `Not Required`.

Gate readiness requires all mandatory controls, evidence for applicable controls, required formal reviews, and no unresolved blocking risk. High or Critical residual risk cannot be treated as approved merely because checklist completion is high; it requires remediation or a documented, authorized, time-bound decision.

## Formal review

Formal review groups are `Cyber`, `Data`, `Application`, `Network`, and `Enterprise`.

```json
{
  "group": "Network",
  "phase": "Design",
  "applicability": "Required",
  "status": "In Review",
  "submittedDate": "2026-10-10",
  "decisionDate": null,
  "conditions": "",
  "evidence": ["Network design reviewed internally"],
  "revalidationRequired": false
}
```

Allowed review statuses are `Not Started`, `In Review`, `Changes Needed`, `Approved`, `Approved with Conditions`, and `Not Required`.

## Technical risk

Technical risk entries belong in `technicalRisks` and must remain public-safe.

```json
{
  "id": "TR-001",
  "title": "Public-safe risk title",
  "category": "AI Reliability",
  "scenario": "Public-safe description of the technical failure scenario and potential impact.",
  "ownerGroup": "Application",
  "status": "Mitigating",
  "inherentRisk": "High",
  "controls": ["DES-08", "DES-09", "DES-10"],
  "mitigation": "Public-safe summary of preventive, detective, and corrective controls.",
  "targetDate": "2026-10-31",
  "residualRisk": "Moderate",
  "decision": "Mitigate before deployment.",
  "decisionDate": null,
  "exceptionExpirationDate": null,
  "evidence": ["Detailed technical assessment reviewed internally"]
}
```

Allowed risk ratings are `Not Assessed`, `Low`, `Moderate`, `High`, and `Critical`. Allowed statuses are `Open`, `Mitigating`, `Monitoring`, `Accepted`, and `Closed`.

The Design assessment should consider data exposure, identity and access, prompt injection, unauthorized retrieval, hallucination, knowledge-source poisoning, unsafe automation, insecure APIs, external connectivity, missing auditability, vendor or model changes, dependency risk, availability, recovery, human oversight, and model or response degradation.

## Decision record

```json
{
  "id": "DEC-001",
  "phase": "Design",
  "type": "Gate Decision",
  "decision": "Public-safe description of the decision.",
  "outcome": "Approved with Conditions",
  "decisionDate": "2026-10-20",
  "decisionByGroup": "Enterprise",
  "conditions": "Public-safe conditions or limitations."
}
```

## Monitoring metric

```json
{
  "id": "MET-001",
  "name": "Validated response quality",
  "ownerGroup": "Data",
  "target": "Approved threshold",
  "current": "Not measured",
  "status": "Not Started",
  "lastMeasuredDate": null,
  "evidence": []
}
```

Update the use case's current phase, current step, health, review status, next decision, and dates in `status.json` whenever the detailed governance record changes.
