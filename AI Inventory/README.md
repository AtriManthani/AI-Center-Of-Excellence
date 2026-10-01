# AI Inventory

Open the **[live AI Inventory dashboard](https://atrimanthani.github.io/AI-Center-Of-Excellence/AI%20Inventory/)** to present the latest approved use-case statuses.

This folder contains the leadership presentation layer and the public, non-sensitive governance workspace. Everything committed here is visible publicly and must be approved for public sharing.

The dashboard automatically discovers published records in `use-cases`. `data/use-cases.json` is the generated fallback. Never add sensitive, confidential, personal, security-restricted, contractual, or legally protected information anywhere in this repository.

## Simple use-case structure

Every use case has one `status.json` file and nine phase folders:

`Intake → Qualify → Prioritize → Design → Develop → Test → Deploy → Monitor → Close`

Upload forms and reviews directly into the matching phase folder. Each phase folder contains a short `CHECKLIST.md`. `status.json` records the current stage and the small sequence of steps inside the current phase. Select **View Status** on a dashboard card to see what is complete, current, and upcoming.
