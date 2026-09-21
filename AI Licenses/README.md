# AI License Management

This folder is the source of truth for the AI CoE license dashboard.

## Update the dashboard

1. Prepare an Excel workbook with one row per user and tool assignment, using the exact columns below.
2. Upload the `.xlsx` file to this folder. The filename and version may change.
3. If replacing the current workbook, remove the old workbook or ensure the new workbook is the most recently committed file.
4. Refresh the [live license dashboard](https://atrimanthani.github.io/AI-Center-Of-Excellence/AI%20Licenses/).

The dashboard automatically selects the most recently updated Excel workbook in this folder. Changes made inside that workbook appear after the updated file is committed to GitHub and the dashboard is refreshed.

## Spreadsheet structure

The dashboard is designed for the structure of `Microsoft Training_2026 (1).xlsx`. The workbook can use any worksheet name, but the following headers must be present within the first 20 rows and should remain in this order:

| Column | Dashboard use |
| --- | --- |
| `User` | Public-safe user reference used to count and group individual license holders. |
| `Department` | Department totals and filtering. |
| `SubDepartment` | Organizational detail in the employee and assignment views. |
| `Email` | Recognized for schema compatibility but never displayed. It must be blank in a public upload. |
| `Training` | Training-status totals and employee-level status. |
| `Training Date` | Training schedule and assignment detail. |
| `Training Class` | Training schedule and assignment detail. |
| `Tool` | License type and tool-allocation totals. Each populated row counts as one issued license. |

Example:

| User | Department | SubDepartment | Email | Training | Training Date | Training Class | Tool |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AI-USER-001` | Public Safety | Administration |  | Scheduled | 2026-09-28 | Class 1 | HR Policies Chatbot |
| `AI-USER-002` | Finance | Accounting |  | No |  |  | HR Policies Chatbot |

## Public-data requirement

This repository is public. Do not upload the supplied workbook unchanged because it contains employee names and email addresses.

Before uploading a future workbook:

- Replace every `User` value with a public-safe reference such as `AI-USER-001`.
- Clear every value in the `Email` column while keeping the column header.
- Do not include personnel numbers or other identifying information.

The dashboard blocks a workbook when it detects email addresses or name-like values in the `User` column.
