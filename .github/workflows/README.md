# Automated checks

`validate-ai-inventory.yml` checks every published use-case `status.json` file whenever inventory records change.

The check prevents unsupported phases, statuses, review labels, checklist records, dates, and issue values from reaching the dashboard.

`validate-license-workbook.yml` checks Excel workbooks in `AI Licenses` for the required nine-column structure, anonymous user references, and blank email values. Use the browser-based Prepare License Workbook page before uploading; validation cannot remove data that was already committed.

`validate-its-project-workbook.yml` checks Excel workbooks in `ITS Project Tracking` for delivery fields, structured risk level/category, and blocks owner columns, detailed risk narratives, review notes, and email-like values. Use Prepare Project Workbook before uploading.
