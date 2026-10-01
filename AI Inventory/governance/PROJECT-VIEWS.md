# Recommended GitHub Project views

When the AI CoE creates a GitHub Project for this repository, use these saved views:

## Governance Pipeline

- Layout: Board
- Column field: Governance Phase
- Filter: `Status:In Progress`
- Card fields: Use Case ID, Health, Risk Tier, Gate Readiness, Current Step, Pending Reviews, Next Decision Date

## Formal Review Queue

- Layout: Table
- Group by: Review Group
- Filter: `Review Status:Not Started,In Review,Changes Needed`
- Fields: Use Case ID, Governance Phase, Review Group, Review Status, Submitted Date, Conditions

## Technical Risk Register

- Layout: Table
- Group by: Residual Risk
- Filter: `Risk Status:Open,Mitigating,Monitoring,Accepted`
- Fields: Risk ID, Use Case ID, Category, Owner Group, Inherent Risk, Residual Risk, Target Date, Decision

## Overdue Governance Actions

- Layout: Table
- Sort by: Target Date ascending
- Filter: `Target Date:<@today -Requirement Status:Complete -Requirement Status:"Not Applicable"`
- Fields: Use Case ID, Governance Phase, Control ID, Owner Group, Requirement Status, Target Date

## Priority Backlog

- Layout: Table
- Filter: `Status:Backlog`
- Group by: Department

## Live Inventory

- Layout: Table
- Filter: `Status:Live`
- Group by: Department

## On Hold

- Layout: Table
- Filter: `Status:"On Hold"`

## Closed

- Layout: Table
- Filter: `Status:Closed`

## Leadership Dates

- Layout: Roadmap
- Date field: Next Decision Date
- Filter: `-Status:Closed`
