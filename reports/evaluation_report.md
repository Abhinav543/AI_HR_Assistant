# AI-Powered Leave, Attendance & Workforce Planning Assistant

# Evaluation and Testing Report

## 1. Project Overview

The project is an AI-powered HR assistant designed to support employee leave management, attendance monitoring, workforce planning, and HR policy information retrieval.

The application combines structured SQLite database operations, deterministic business rules, Retrieval-Augmented Generation (RAG), FAISS vector search, and a locally hosted Ollama language model.

The system provides employee self-service functionality, policy question answering, manager decision support, and workforce analytics.

Final leave approval and rejection remain the responsibility of authorized managers or HR personnel. The AI assistant does not independently make employment decisions.

## 2. Testing Objectives

The objectives of testing are:

- Verify employee leave balance calculations.
- Validate leave request submission and approval workflows.
- Check overlapping leave and notice-period rules.
- Verify holiday and comp-off calculations.
- Evaluate HR policy retrieval and source references.
- Check employee-specific chatbot responses.
- Evaluate manager dashboards and workforce planning features.
- Verify that unsupported policy questions receive appropriate responses.
- Verify policy version handling and policy index refresh.
- Evaluate timeline alerts and deadline tracking.

## 3. Test Environment

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| RAG Framework | Custom RAG pipeline |
| Vector Search | FAISS |
| Embedding Model | all-MiniLM-L6-v2 |
| Language Model | Qwen2.5:0.5b |
| LLM Runtime | Ollama |
| Operating System | Windows |

Testing was performed using synthetic employee, leave, attendance, holiday, comp-off, and project data.

## 4. Test Cases and Results

### Status Definitions

- **Passed:** Test was executed and the expected behaviour was observed.
- **Pending:** Test has not yet been fully verified or its actual result has not been recorded.
- **Failed:** Test was executed and did not produce the expected result.

| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC01 | Sufficient leave balance and notice period | Request should satisfy applicable validation rules and be saved as Pending | Priya's annual leave request was saved as Pending and eligibility was evaluated successfully | Passed |
| TC02 | Leave request exceeds available balance | System should identify insufficient leave balance | Not yet recorded | Pending |
| TC03 | Overlapping leave request | System should detect overlapping requests | Not yet recorded | Pending |
| TC04 | Insufficient notice period | System should flag notice-period violation | Not yet recorded | Pending |
| TC05 | Leave period includes weekends and holidays | Working days should exclude weekends and configured holidays | Not yet recorded | Pending |
| TC06 | Comp-off approaching expiry | System should identify upcoming expiry | Not yet recorded as a functional test result | Pending |
| TC07 | Expired comp-off usage | System should prevent invalid usage | Not yet recorded | Pending |
| TC08 | Duplicate comp-off usage | System should prevent reuse of an already-used record | Not yet recorded | Pending |
| TC09 | HR policy question covered by documents | Chatbot should retrieve relevant policy information and sources | Chatbot returned the applicable annual leave entitlement of 20 days and notice period of 5 calendar days from Policy Version 2.0 | Passed |
| TC10 | HR policy question not covered by documents | Chatbot should indicate insufficient policy information | Chatbot indicated that the available policy documents did not specify the carry-forward rule before the policy was expanded | Passed |
| TC11 | Manager approval or rejection | Manager action should update the request status | Not yet recorded as a complete test result | Pending |
| TC12 | Project deadline and backup analysis | System should identify potential leave conflicts and backup information | Not yet recorded as a complete test result | Pending |
| TC13 | Employee asks for annual leave balance | Displays entitlement, used, pending and remaining leave | Correct employee balance displayed | Passed |
| TC14 | Employee asks for sick leave balance | Displays sick leave balance from database | Correct sick leave balance displayed | Passed |
| TC15 | Employee asks for leave history | Displays employee leave requests and statuses | Leave history displayed correctly | Passed |
| TC16 | Employee asks for pending leave | Displays only pending leave requests | Pending requests displayed correctly | Passed |
| TC17 | Employee asks about annual leave entitlement | Retrieves entitlement from applicable HR policy | Correct policy entitlement displayed | Passed |
| TC18 | Employee asks about annual leave carry-forward | Explains carry-forward limit, usage period, expiry and sick leave exclusion | Chatbot successfully retrieved and answered using the newly added sample policy section | Passed |
| TC19 | Employee asks about comp-off policy | Explains eligibility, approval, usage and expiry | Chatbot response was tested; detailed result not independently recorded | Pending |
| TC20 | Employee asks about public holidays during leave | Explains exclusion of official holidays and weekends from leave-day calculations | Not yet recorded | Pending |
| TC21 | Employee asks about required documents and approvals | Explains request information, medical certificate conditions and approval responsibilities | Chatbot question was submitted; detailed response not recorded | Pending |
| TC22 | Employee asks about delayed manager approval | Explains overdue request handling and HR escalation | Not yet recorded | Pending |

**Note:** Passing a chatbot question-answering test does not automatically verify the corresponding structured leave-management or comp-off functionality. Those functional scenarios are tracked separately.

## 5. RAG Chatbot Evaluation

The HR chatbot was evaluated using employee-specific questions and policy-related questions.

### 5.1 Employee-Specific Questions

The following capabilities were confirmed during application testing:

- Retrieval of annual leave balances from SQLite.
- Retrieval of sick leave balances from SQLite.
- Display of employee leave history.
- Filtering of pending leave requests.
- Retrieval of annual leave entitlement from the applicable HR policy.

Employee-specific numerical information is retrieved through structured database operations rather than generated by the language model.

### 5.2 Policy Knowledge Retrieval

The RAG pipeline uses:

1. HR policy document loading.
2. Text extraction and chunking.
3. Sentence Transformer embeddings.
4. FAISS vector indexing and similarity search.
5. Relevant policy context retrieval.
6. Local Qwen model response generation through Ollama.

The chatbot supports policy questions covering:

- Annual and sick leave entitlement.
- Planned leave notice requirements.
- Carry-forward of unused leave.
- Compensatory-off rules.
- Public holidays during leave.
- Required documents and approval procedures.
- Escalation for delayed manager approvals.

### 5.3 Policy Version Handling

Two sample HR policy versions are maintained.

| Policy Version | Effective Date | Annual Leave | Sick Leave | Annual Leave Notice |
|---|---|---:|---:|---:|
| Version 1.0 | 1 January 2026 | 18 days | 10 days | 3 calendar days |
| Version 2.0 | 1 November 2026 | 20 days | 12 days | 5 calendar days |

The chatbot supports comparison of policy versions and effective-date-based policy selection.

### 5.4 Unsupported Questions

The chatbot uses a retrieval similarity threshold and fallback response to handle questions not sufficiently supported by the available policy documents.

It is designed to communicate when the policy set does not provide an answer instead of inventing unsupported HR rules.

### 5.5 Policy Updates

Policy documents can be updated and the FAISS policy index refreshed using the implemented refresh function.

The updated policy content is then available to the retrieval pipeline.

## 6. Performance and Reliability Considerations

The application uses local database storage and a locally hosted language model.

Performance depends on:

- Available system memory.
- Embedding generation.
- FAISS retrieval.
- Local language model inference.
- Database query execution.

The system uses deterministic calculations for leave balances, working days, and validation rather than relying on generated AI responses.

The local model may produce incomplete responses, so retrieved policy sources should be reviewed.

## 7. Assumptions and Limitations

### 7.1 Assumptions

- All employee records and HR data are synthetic.
- Annual leave notice period under Policy Version 2.0 is 5 calendar days.
- Sick leave notice is configured as 0 days in the application logic.
- Approval deadline is 2 working days as a demonstration assumption.
- Team coverage threshold is 50% as a demonstration assumption.
- Comp-off expiry warning window is 30 days.
- Weekdays are considered working days except configured holidays.
- Employee-specific leave balances are maintained through structured sample records.

### 7.2 Sample Policy Assumptions

Additional demonstration policy rules include:

- A maximum of 5 unused annual leave days may be carried forward.
- Carried-forward leave must be used within the first 3 months of the following calendar year.
- Carried-forward leave expires after 31 March.
- Sick leave cannot be carried forward.
- Approved extra working days may earn compensatory off.
- Comp-off must be used before its recorded expiry date.
- Official company holidays and weekends are excluded from leave-day calculations.
- A medical certificate is required for sick leave exceeding 2 consecutive working days.
- Pending approvals exceeding the configured review period are flagged for HR follow-up.

These are sample rules created for demonstration and assessment purposes, not verified real-world company policies.

### 7.3 Limitations

- The application uses SQLite for demonstration purposes.
- Approval decisions are simulated through the manager interface.
- Manager authentication is limited to the implemented demonstration role-selection workflow.
- Email and SMS notifications are not integrated.
- Workforce recommendations depend on configured coverage thresholds and available backup assignments.
- The local language model may produce incomplete answers.
- The application is a prototype and has not been deployed as a production HR system.

## 8. Privacy and Security

- Only synthetic employee information is used.
- The application uses a local SQLite database.
- The language model runs locally through Ollama.
- The demonstration application does not connect to a real HR system.
- Manager and employee roles are simulated for demonstration purposes.
- Production deployment would require authentication, authorization, audit logging, encryption, and additional security controls.

## 9. Conclusion

The AI-Powered Leave, Attendance & Workforce Planning Assistant demonstrates an integrated HR management solution combining structured data processing, deterministic leave calculations, policy document retrieval, employee self-service, and workforce analytics.

The application provides employee leave management, policy question answering, attendance insights, comp-off tracking, timeline monitoring, and workforce planning recommendations through a centralized Streamlit interface.

The confirmed test cases demonstrate employee-specific chatbot functionality, policy entitlement retrieval, policy fallback behaviour, leave request submission, and retrieval of newly added sample policy information.

Remaining functional and policy test cases are clearly identified as pending for further verification.

The project demonstrates how AI-based retrieval can complement structured business logic while keeping final leave approval decisions under human manager or HR control.