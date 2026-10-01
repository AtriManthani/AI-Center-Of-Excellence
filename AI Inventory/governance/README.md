# Governance lifecycle

The workspace uses short labels while remaining mapped to the official Governance Playbook:

| Simple label | Governance Playbook phase |
|---|---|
| Intake | Opportunity Identification |
| Qualify | Opportunity Qualification |
| Prioritize | Opportunity Prioritization |
| Design | Solution Design |
| Develop | Solution Development |
| Test | Solution Testing |
| Deploy | Solution Deployment |
| Monitor | Solution Monitoring & Improvement |
| Close | Solution Closeout |

Validation is part of Develop. Pilot is part of Test.

The checklists in this folder make the Playbook's gate expectations visible. They are advisory: authorized AI CoE administrators may advance a use case while requirements remain incomplete, provided the current gaps are recorded.

`controls.json` is the structured control catalog used by validation and the dashboard. Each control has a stable ID so manually uploaded forms, evidence, reviews, risks, and decisions can be linked to the exact governance requirement they support.

Each use case keeps its leadership summary in `status.json` and its detailed lifecycle record in `governance.json`. The detailed record tracks all nine phases, formal Cyber, Data, Application, Network, and Enterprise reviews, technical risks, gate decisions, exceptions, and production monitoring.

The repository is currently public. Record only public-safe summaries and evidence here. A label such as "Reviewed internally" may be used to acknowledge an internal artifact without publishing the artifact or sensitive technical findings.
