# AI-Powered Leave, Attendance & Workforce Planning Assistant

## 1. Project Overview

The AI-Powered Leave, Attendance & Workforce Planning Assistant is an HR management application designed to simplify employee leave management, attendance monitoring, HR policy queries, and workforce planning.

The application combines structured database operations, deterministic business rules, analytics, and Retrieval-Augmented Generation (RAG) to provide employees and managers with HR information and decision support.

It uses a locally hosted language model to answer HR policy questions, while deterministic Python logic handles leave calculations, balance validation, attendance analysis, comp-off tracking, and workforce availability.

**Important:** The system provides recommendations and decision support. Final leave approval and rejection remain the responsibility of authorized managers or HR personnel. The AI assistant does not independently make employment decisions.

## 2. Project Objectives

- Automate employee leave request submission and tracking.
- Calculate leave balances and working days.
- Provide an AI-powered HR policy chatbot using RAG.
- Monitor employee attendance and leave trends.
- Track compensatory-off balances, usage, and expiry.
- Identify team availability and potential staffing risks.
- Monitor project deadlines and backup assignments.
- Provide managers with a centralized HR dashboard.
- Maintain a timeline of leave events, deadlines, and alerts.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Frontend | Streamlit |
| Database | SQLite |
| Data processing | Pandas, NumPy |
| Visualization | Plotly |
| Language model | Qwen 2.5 (0.5B) |
| Local LLM runtime | Ollama |
| Text embeddings | Sentence Transformers |
| Vector search | FAISS |
| Document processing | PyPDF and text processing |
| Version control | Git and GitHub |

## 4. System Architecture

The application follows a modular architecture.

```text
              Employee / Manager / HR
                       |
                       v
                Streamlit Interface
                       |
          +------------+-------------+
          |            |             |
          v            v             v
     Leave Module   RAG Module   Analytics Module
          |            |             |
          v            v             v
    Business Rules  Embeddings   Data Analysis
          |            |             |
          v            v             v
    SQLite Database  FAISS Index  Visual Reports
          |
          v
  Timeline and Workforce Planning
```

### Application Data Flow

1. Employees and managers interact with the Streamlit interface.
2. Structured HR information is stored and retrieved using SQLite.
3. Python business logic validates leave requests and calculates balances.
4. The RAG module retrieves relevant HR policy sections using FAISS.
5. The local Qwen model generates policy-related responses using retrieved context.
6. Analytics modules process attendance, leave, and workforce data.
7. The timeline module tracks important dates and generates alerts.
8. Managers review recommendations and record final decisions.

## 5. Main Features

### 5.1 Employee Dashboard

- Employee-specific leave balance.
- Annual and sick leave requests.
- Leave request history and status.
- HR policy chatbot.
- Comp-off balance and records.
- Comp-off usage validation.

### 5.2 Leave Management

- Leave request submission.
- Working-day calculation.
- Weekend and holiday exclusion.
- Available, approved-used, and pending leave tracking.
- Overlapping leave detection.
- Notice-period validation.
- Leave eligibility recommendations.
- Manager review and decision recording.

### 5.3 RAG-Based HR Policy Knowledge Assistant

The chatbot allows employees and managers to ask natural-language questions about HR policies.

Supported policy topics include:

- Annual and sick leave entitlement.
- Notice required for planned leave.
- Carry-forward of unused annual leave.
- Compensatory-off eligibility, usage, and expiry.
- Public holidays during leave periods.
- Required documents and approval procedures.
- Escalation for delayed manager approvals.

#### RAG Implementation Workflow

1. Load HR policy documents from the policy directory.
2. Extract policy text.
3. Divide documents into meaningful text chunks.
4. Generate text embeddings using Sentence Transformers.
5. Store and search embeddings using FAISS.
6. Retrieve relevant policy sections for a user query.
7. Provide retrieved context to the local Qwen model through Ollama.
8. Generate an answer with relevant policy source information.

The chatbot also supports:

- Policy version comparison.
- Effective-date-based policy selection.
- Retrieval of relevant policy sections.
- Responses when the available policy documents do not contain an answer.
- Policy index refresh after document updates.

The chatbot is designed to avoid inventing unsupported HR rules. When information is unavailable in the policy documents, it should communicate that limitation.

#### Sample Policy Versions

| Policy version | Effective date | Annual leave | Sick leave | Annual leave notice |
|---|---|---:|---:|---:|
| Version 1.0 | 1 January 2026 | 18 days | 10 days | 3 calendar days |
| Version 2.0 | 1 November 2026 | 20 days | 12 days | 5 calendar days |

Version 2.0 is the applicable policy for dates on or after 1 November 2026. The chatbot can compare policy versions and identify differences in their rules and effective dates.

#### Additional Sample Policy Sections

The latest Version 2.0 document includes demonstration rules for:

- Carry-forward of up to 5 unused annual leave days, subject to the documented expiry conditions.
- Comp-off eligibility, approval, usage, and expiry.
- Exclusion of weekends and official company holidays from leave-day calculations.
- Required leave request information and medical certificate conditions.
- Manager and HR approval responsibilities.
- Escalation when a leave request remains unanswered beyond the configured review period.

These additional rules are explicitly identified as sample/demo policies created for this assessment.

### 5.4 Attendance Analytics

- Overall attendance percentage.
- Employee-wise attendance analysis.
- Department-wise attendance comparison.
- Monthly attendance trends.
- Present, absent, and work-from-home summaries.

**Attendance metric definition:**

Attendance percentage is calculated using:

```text
Attendance Percentage =
(Present Records + WFH Records) / Total Attendance Records * 100
```

Work-from-home records count as attendance in this demonstration.

### 5.5 Leave Analytics

- Total leave requests.
- Approved, pending, and rejected requests.
- Leave type distribution.
- Department-wise leave analysis.
- Employee-wise leave analysis.
- Monthly leave trends.
- Pending requests by department.

Leave analytics use structured leave request records from the SQLite database.

### 5.6 Comp-Off Management

- Earned comp-off balance.
- Available and used comp-off.
- Expired and expiring comp-off.
- Employee-specific comp-off records.
- Validation before usage.
- Prevention of repeated usage of the same record.

Comp-off usage is validated using structured database records rather than AI-generated calculations.

### 5.7 Timeline and Deadline Management

The timeline module tracks:

- Leave start and end dates.
- Leave request submission.
- Approval deadlines.
- Return-to-work dates.
- Comp-off earning and expiry.
- Company holidays.
- Project deadlines.

It also identifies:

- Overdue leave approvals.
- Expiring and expired comp-off records.
- Upcoming project deadlines.
- Overlapping team leave.

Timeline events are stored in the SQLite database and can be viewed through the manager dashboard.

### 5.8 Workforce Planning

- Department-wise employee availability.
- Planned employee absences.
- Team coverage percentage.
- Project deadline risk analysis.
- Backup employee assignments.
- Workforce planning recommendations.

The application flags potential staffing risks when employee absences overlap with important project deadlines.

Recommendations consider available employee and backup information. Missing backup assignments can be highlighted as risks.

### 5.9 Manager / HR Dashboard

Managers and HR personnel can:

- View pending leave requests.
- Review leave eligibility and supporting information.
- Record simulated approval or rejection decisions.
- Monitor attendance and leave analytics.
- Review comp-off records.
- Monitor timeline alerts.
- Identify potential workforce and project risks.

Final leave decisions remain with authorized managers or HR representatives.

## 6. Project Structure

```text
AI_HR_Assistant/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── employees.csv
│   ├── attendance.csv
│   ├── leave_requests.csv
│   ├── holidays.csv
│   └── comp_off.csv
│
├── documents/
│   └── hr_policies/
│       ├── leave_policy_v1.txt
│       └── leave_policy_v2.txt
│
├── database/
│   └── hr_assistant.db
│
├── src/
│   ├── data_processing/
│   ├── database/
│   ├── leave_management/
│   ├── rag/
│   ├── decision_engine/
│   └── analytics/
│
├── tests/
│   └── test_scenarios.md
│
└── reports/
    └── evaluation_report.md
```

The project also contains supporting Python modules for policy processing, leave calculations, database operations, analytics, and timeline management.

## 7. Database and Sample Data

SQLite is used for persistent storage.

The database includes tables for:

- Employees.
- Leave requests.
- Attendance.
- Holidays.
- Comp-off records.
- Leave decisions.
- Project deadlines.
- Backup assignments.
- Timeline events.

### Sample Data

The project uses fictional employee information and synthetic HR records.

The sample datasets include:

- 10 employees across multiple departments.
- Attendance records.
- Leave requests with different statuses.
- Company holidays.
- Comp-off records.
- Project deadline and backup information.

### Leave Balance Assumption

Employee-specific leave balances are maintained through structured employee records. The policy documents describe standard policy entitlements, while the employee records provide the sample balance data used by the application.

These are demonstration records and should be reconciled with the applicable policy before any real-world use.

## 8. Installation and Execution

### Prerequisites

- Python 3.10 or later.
- Git.
- Ollama.
- Qwen 2.5 (0.5B) model.

### Step 1: Clone the Repository

```bash
git clone <YOUR_PRIVATE_GITHUB_REPOSITORY_URL>
cd AI_HR_Assistant
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Install the additional RAG dependencies:

```bash
pip install sentence-transformers faiss-cpu
```

### Step 5: Install and Start Ollama

Download the Qwen model:

```bash
ollama pull qwen2.5:0.5b
```

Ensure the Ollama service is running before using the policy chatbot.

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in the browser.

### Step 7: Refresh the Policy Index After Updates

After modifying HR policy documents, refresh the FAISS index using:

```powershell
python -c "from src.rag.rag_assistant import refresh_policy_index; refresh_policy_index(); print('Policy index refreshed successfully!')"
```

Restart the Streamlit application if necessary to use the refreshed policy index.

## 9. Business Rules and Assumptions

The following rules are used for this demonstration. They should not be interpreted as universal HR policies.

| Rule | Implementation / Assumption |
|---|---|
| Annual leave entitlement | Policy-version dependent |
| Sick leave entitlement | Policy-version dependent |
| Annual leave notice | 5 calendar days under Version 2.0 |
| Sick leave notice | 0 days in the application logic |
| Approval SLA | 2 working days |
| Team coverage threshold | 50% |
| Comp-off expiry alert | Within 30 days |
| Working days | Weekdays excluding configured holidays |
| Return-to-work date | Next working day after leave ends |

### Leave Calculations

Leave balance and eligibility calculations use deterministic Python functions rather than relying on LLM-generated calculations.

The application considers:

- Employee leave entitlement.
- Approved leave already used.
- Pending leave requests.
- Requested leave duration.
- Weekends and company holidays.
- Notice-period requirements.
- Overlapping leave requests.

Pending requests are tracked separately from approved leave usage.

### Workforce Planning

The application uses a 50% team coverage threshold as a demonstration assumption. It is not a universal staffing policy.

### Comp-Off

Comp-off expiry and usage are validated against stored records. The 30-day warning window is a demonstration configuration.

### Approval

The 2-working-day approval SLA is a demonstration assumption. An overdue request is flagged for attention and does not automatically become approved or rejected.

## 10. Testing and Evaluation

Functional test scenarios are documented in:

```text
tests/test_scenarios.md
```

The test plan covers:

- Sufficient leave balance.
- Insufficient leave balance.
- Overlapping leave requests.
- Notice-period violations.
- Weekend and holiday calculations.
- Comp-off expiry.
- Expired comp-off prevention.
- Duplicate comp-off usage prevention.
- HR policy chatbot responses.
- Questions not covered by policy documents.
- Manager approval and rejection.
- Project deadline and backup analysis.
- Annual and sick leave balance queries.
- Employee leave history.
- Pending leave queries.
- Policy entitlement questions.
- Newly added HR policy topics.

### Test Results

Actual results and pass/fail statuses are maintained in the functional test report.

Only test cases that have been executed and verified should be marked as Passed. Pending or unverified cases must remain clearly identified.

The evaluation report is maintained separately:

```text
reports/evaluation_report.md
```

It documents the testing approach, results, assumptions, and known limitations.

## 11. Privacy and Security

- Only synthetic employee information is used.
- The application uses a local SQLite database.
- The language model runs locally through Ollama.
- The demonstration application does not connect to a real HR system.
- Employee and manager roles are simulated for demonstration purposes.
- Production deployment would require authentication, authorization, audit logging, encryption, and additional security controls.

## 12. Limitations

- Sample datasets are synthetic and limited in size.
- Manager authentication is simulated.
- Approval notifications are not connected to email or SMS.
- Workforce recommendations depend on configured coverage thresholds and available backup assignments.
- The local language model may produce incomplete answers; policy sources should be reviewed.
- Policy rules are sample demonstration rules, not verified company policies.
- The application is a demonstration prototype, not a production HR platform.

## 13. Future Enhancements

- Role-based authentication and access control.
- Calendar integration.
- Email and notification support.
- Advanced policy version comparison.
- Improved hybrid retrieval and reranking.
- Workforce what-if analysis.
- Audit logs and reporting.
- Production database integration.

## 14. Conclusion

The AI-Powered Leave, Attendance & Workforce Planning Assistant demonstrates how AI, Retrieval-Augmented Generation, structured databases, deterministic business rules, and analytics can be combined to support HR operations.

The application provides employee leave management, policy question answering, attendance insights, comp-off tracking, timeline monitoring, and workforce planning recommendations through a centralized Streamlit interface.

The project emphasizes explainable recommendations, structured calculations, policy-based information retrieval, and human oversight for final HR decisions.