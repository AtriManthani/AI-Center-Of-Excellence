# AI License Management

This folder is the source of truth for the AI CoE license dashboard.

## Update the dashboard

1. Open **[Prepare License Workbook](https://atrimanthani.github.io/AI-Center-Of-Excellence/AI%20Licenses/prepare.html)**.
2. Select the original `.xlsx` workbook on your computer.
3. Download the generated file beginning with `AI_License_Register_Public_`.
4. Delete the previous `.xlsx` file from this folder and upload only the prepared file.
5. Commit the upload and refresh the [live license dashboard](https://atrimanthani.github.io/AI-Center-Of-Excellence/AI%20Licenses/).

The dashboard automatically selects the most recently updated Excel workbook in this folder. Changes made inside that workbook appear after the updated file is committed to GitHub and the dashboard is refreshed.

## Spreadsheet structure

The dashboard is designed for the current Microsoft Training workbook structure. The workbook can use any worksheet name, but the following headers must be present within the first 20 rows:

| Column | Dashboard use |
| --- | --- |
| `User` | Public-safe user reference used to count and group individual license holders. |
| `Department` | Department totals and filtering. |
| `SubDepartment` | Organizational detail in the employee and assignment views. |
| `Email` | Recognized for schema compatibility but never displayed. It must be blank in a public upload. |
| `Training` | Training-status totals and employee-level status. |
| `Training Date` | Training schedule and assignment detail. |
| `License Type` | License-category totals and employee-level allocation. |
| `License Provision Date` | Determines whether a license is issued. A populated date counts as issued; a blank date counts as not yet issued. |
| `Tool` | Tool-allocation totals. Each populated row counts as one issued license. |

Example:

| User | Department | SubDepartment | Email | Training | Training Date | License Type | License Provision Date | Tool |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `AI-USER-001` | Public Safety | Administration |  | Scheduled | 2026-09-28 | Premium | 2026-09-20 | HR Policies Chatbot |
| `AI-USER-002` | Finance | Accounting |  | No |  | Premium | 2026-09-20 | HR Policies Chatbot |

## Public-data requirement

This repository is public. Do not upload the supplied workbook unchanged because it contains employee names and email addresses.

Never upload the original Microsoft Training workbook directly. Use **Prepare License Workbook** first. It runs locally in the browser, replaces each `User` value with a public-safe reference, clears every `Email` value, preserves the reporting fields, and downloads a separate safe copy. The original file is not changed or uploaded by the preparation page.

The dashboard continues to block any workbook containing email addresses or name-like values as a final safeguard.

## Issuance rule

The dashboard does not count every workbook row as an issued license. A license is counted as **issued only when `License Provision Date` is populated**. Records with a blank provisioning date remain visible in the total and assignment detail but are reported as **not yet issued**.
