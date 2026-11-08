# AI-Powered Leave, Attendance & Workforce Planning Assistant
## Functional Test Report

**Testing approach:** Functional testing using synthetic employee, leave, attendance, holiday, comp-off, and project data.

**Environment:** Python, Streamlit, SQLite, local Ollama model.

| Test ID | Test scenario | Expected result | Actual result | Status |
|---|---|---|---|---|
| TC01 | Employee requests leave with sufficient balance and notice | Request is saved as Pending and eligibility is evaluated | To be recorded | Pending |
| TC02 | Employee requests more leave than their remaining balance | System flags insufficient leave balance | To be recorded | Pending |
| TC03 | Employee submits overlapping leave dates | System detects the overlapping request | To be recorded | Pending |
| TC04 | Employee submits annual leave without sufficient notice | System flags the notice-period violation | To be recorded | Pending |
| TC05 | Leave period includes weekends or company holidays | Working-day calculation excludes weekends and holidays | To be recorded | Pending |
| TC06 | Employee has a comp-off record approaching expiry | System displays the expiring comp-off alert | To be recorded | Pending |
| TC07 | Employee attempts to use an expired comp-off record | System prevents comp-off usage | To be recorded | Pending |
| TC08 | Employee attempts to use the same comp-off twice | First use succeeds; subsequent use is rejected | To be recorded | Pending |
| TC09 | Employee asks a question covered by the HR policy documents | RAG assistant answers using policy context and displays its source | To be recorded | Pending |
| TC10 | Employee asks a question not covered by the HR policies | Assistant indicates that the available policy documents do not provide an answer | To be recorded | Pending |
| TC11 | Manager reviews a pending leave request | Manager can record an approval or rejection decision | To be recorded | Pending |
| TC12 | Employee's leave overlaps with a project deadline | Workforce risk analysis flags the potential conflict and shows backup information where available | To be recorded | Pending |

## Testing Notes

- All test employees and records are synthetic.
- Leave balances and working-day calculations are handled through structured data and deterministic logic.
- Policy answers are retrieved from the indexed HR policy documents.
- AI recommendations do not independently approve or reject leave requests.
- Final leave decisions remain with the authorized manager or HR representative.
- Actual results and statuses must be updated after executing each test case.

## Known Demo Assumptions

- Annual leave notice period: 5 calendar days under policy version 2.0.
- Approval deadline: 2 working days (demo assumption).
- Team coverage threshold: 50% (demo assumption).
- Comp-off expiry warning window: 30 days (demo assumption).


| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC13 | Employee asks for annual leave balance | Displays entitlement, used, pending and remaining leave | Correct employee balance displayed | Passed |
| TC14 | Employee asks for sick leave balance | Displays sick leave balance from database | Correct sick leave balance displayed | Passed |
| TC15 | Employee asks for leave history | Displays employee leave requests and statuses | Leave history displayed correctly | Passed |
| TC16 | Employee asks for pending leave | Displays only pending leave requests | Pending requests displayed correctly | Passed |
| TC17 | Employee asks about annual leave entitlement | Retrieves entitlement from applicable HR policy | Correct policy entitlement displayed | Passed |
