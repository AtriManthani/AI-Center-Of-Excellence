# AI License Management

This folder is the source of truth for the AI CoE license dashboard.

## Update the dashboard

1. Prepare an Excel workbook with one row per employee and license type.
2. Upload the `.xlsx` file to this folder. The filename and version may change.
3. If replacing the current workbook, remove the old workbook or ensure the new workbook is the most recently committed file.
4. Refresh the [live license dashboard](https://atrimanthani.github.io/AI-Center-Of-Excellence/AI%20Licenses/).

The dashboard automatically selects the most recently updated Excel workbook in this folder. Changes made inside that workbook appear after the updated file is committed to GitHub and the dashboard is refreshed.

## Spreadsheet structure

The workbook can use any worksheet name. Put the column headers within the first 20 rows.

Required columns:

| Column | Purpose |
| --- | --- |
| `Employee ID` | Non-sensitive employee reference used to group licenses by employee. `Employee Reference` or `User ID` also works. |
| `License Type` | License product, SKU, or subscription name. `License`, `Product`, or `SKU` also works. |

Optional columns:

| Column | Purpose |
| --- | --- |
| `Quantity` | Number issued on that row. Defaults to `1`. `License Count` or `Seats` also works. |
| `Department` | Enables department filtering. |
| `Status` | `Returned`, `Revoked`, `Removed`, `Cancelled`, and `Expired` records are excluded from current issued totals. All other values are treated as currently issued. |
| `Assigned Date` | Assignment date shown in the detailed view. |
| `Expiration Date` | Expiration or renewal date shown in the detailed view. |

Example:

| Employee ID | Department | License Type | Quantity | Status | Assigned Date |
| --- | --- | --- | ---: | --- | --- |
| `EMP-001` | Public Safety | Microsoft 365 Copilot | 1 | Issued | 2026-09-01 |
| `EMP-001` | Public Safety | Power BI Pro | 1 | Issued | 2026-09-01 |
| `EMP-002` | Finance | Microsoft 365 Copilot | 1 | Issued | 2026-09-05 |

## Public-data requirement

This repository is public. Do not upload employee names, email addresses, personnel numbers, or other sensitive information. Use a non-sensitive employee reference approved for public reporting.
