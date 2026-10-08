# AI Test Report
**Project Title:** Certificate Request System  
**Institution:** Sri Eshwar College of Engineering  
**Assessment:** Software Engineering SAT II Assessment  

---

## 1. Testing Summary
The Certificate Request System underwent automated verification using `pytest` covering all mandatory test requirements (T1 through T12) defined in the Software Engineering SAT II specification. Testing evaluated active request limits (BR1), rechecked eligibility and resource capacity (BR2), master data snapshot immutability (BR3), statutory charge calculation (BR4), input validation (BR5), atomic rollback on partial failure (BR6), atomic success transaction (BR7), sequential administrative status progression and skipping prevention (BR8), user cancellation and single-time quota release (BR9), role-based and ownership access control (BR10), and database persistence across application restarts.

## 2. Environment
- **Operating System:** Windows 11 (win32)
- **Python Version:** 3.14.3
- **Test Runner:** `pytest 9.1.1` (pluggy 1.6.0)
- **Database Engine:** SQLite 3 (Persistent relational file `database.db` with WAL/Foreign Keys enabled)
- **Web Framework:** Flask 3.0.3, Jinja2 3.1.6, Werkzeug 3.1.8

## 3. Number of Tests
- **Total Test Cases Implemented:** 22 automated test functions spanning 10 dedicated test suites.
- **Coverage:** 100% of specified Functional Requirements (FR1 - FR10) and Business Rules (BR1 - BR10).

## 4. Passed
- **22 tests passed** (100% pass rate).

## 5. Failed
- **0 tests failed**.

## 6. Not Run
- **0 tests skipped / not run**.

---

## 7. AI-Assisted Development
The system was designed and synthesized using conversational AI engineering to adhere strictly to Software Engineering SAT II requirements. AI was employed to structure the clean MVC architecture, generate declarative SQL schemas, create atomic transaction boundaries, write parameterized pytest suites, and build responsive, accessible college-branded Jinja2 templates without unnecessary external library bloat.

## 8. Representative AI Prompts
1. *"Generate an atomic SQLite transaction in Python that reserves resource capacity, inserts a certificate request with historical snapshot fields, and creates a status history record, rolling back completely if any step fails."*
2. *"Implement exact business rule BR4 for fee calculation: amount < 1000 => Rs.50, amount >= 1000 => Rs.0, with boundary tests for 999, 1000, 1001."*
3. *"Construct a strict status transition dictionary for administrators ensuring requests cannot skip states from SUBMITTED to IN_PROGRESS or COMPLETED."*
4. *"Create a test for BR9 verifying that repeated cancellation attempts on an already CANCELLED request produce an error and release resource capacity exactly once."*

## 9. AI Suggestions Accepted
- **Separation of Concerns:** Isolated `ValidationService` for stateless business rule logic and `RequestService` for transactional database workflows.
- **Context Management for Transactions:** Used SQLite connection context managers (`with conn:`) to ensure guaranteed atomicity and automatic rollback upon any unhandled exception.
- **Client-Side Live Preview with Independent Server Validation:** Provided interactive JavaScript fee and capacity feedback while strictly enforcing server-side revalidation before database commits.
- **Master Data Snapshot Pattern:** Captured explicit snapshot columns (`service_name_snapshot`, `service_value_snapshot`) rather than joining live master tables for historical records.

## 10. AI Suggestions Corrected
- **Windows File Handle Locking:** Initial test teardowns on Windows encountered `PermissionError` when deleting temporary SQLite files due to active connection references in test assertions. The connection lifecycle in tests was explicitly bounded and closed before cleanup.
- **Form Coercion Consistency:** Ensured amount inputs gracefully handled empty strings, whitespace, and negative values before feeding into charge calculation.

## 11. Defects Found
- `DEF-001`: Teardown failure during pytest execution on Windows operating systems due to unclosed database connection references holding OS file locks.

## 12. Defects Fixed
- All database connections created in test helper assertions were made explicit and closed in `finally` blocks, and `gc.collect()` was invoked in `tests/conftest.py`.

## 13. Retesting
- Executed `python -m pytest -v` across all suites:
  ```
  tests/test_all_requirements.py::test_t5_complete_valid_submission_atomic_success PASSED
  tests/test_all_requirements.py::test_t11_database_persistence_after_application_restart PASSED
  tests/test_all_requirements.py::test_complete_demo_workflow_end_to_end PASSED
  tests/test_br10_access.py::test_t8_user_cannot_access_or_cancel_another_users_request PASSED
  tests/test_br10_access.py::test_t8_user_cannot_perform_admin_actions PASSED
  tests/test_br10_access.py::test_t8_route_access_control PASSED
  tests/test_br1_active_limit.py::test_t2_active_request_limit_4_5_6 PASSED
  tests/test_br1_active_limit.py::test_completed_and_cancelled_do_not_count_toward_active_limit PASSED
  tests/test_br2_eligibility.py::test_t3_inactive_service_s103 PASSED
  tests/test_br2_eligibility.py::test_t7_change_eligibility_resource_before_acceptance PASSED
  tests/test_br2_eligibility.py::test_inactive_user_rejected PASSED
  tests/test_br3_snapshot.py::test_t12_change_master_data_after_request_snapshot_immutable PASSED
  tests/test_br4_charge.py::test_t4_charge_boundary_values PASSED
  tests/test_br5_validation.py::test_t6_blank_name_rejected PASSED
  tests/test_br5_validation.py::test_t6_invalid_phone_rejected PASSED
  tests/test_br5_validation.py::test_t6_missing_description_and_reference PASSED
  tests/test_br6_no_partial_update.py::test_t6_br6_no_partial_update_on_validation_failure PASSED
  tests/test_br6_no_partial_update.py::test_t1_no_duplicate_incorrect_records PASSED
  tests/test_br8_status.py::test_t9_admin_valid_status_progression PASSED
  tests/test_br8_status.py::test_t9_admin_skipping_stages_fails PASSED
  tests/test_br9_cancellation.py::test_t10_cancellation_and_repeated_cancellation PASSED
  tests/test_br9_cancellation.py::test_cannot_cancel_non_submitted_request PASSED
  ============================= 22 passed in 1.81s ==============================
  ```

## 14. Limitations
- Production features such as multi-factor authentication (MFA), password salting/hashing (bcrypt/argon2), email/SMS notifications, and PDF certificate export are intentionally omitted to keep the academic prototype lightweight, demonstrable, and viva-ready.

## 15. Production Improvements
1. Implement bcrypt-hashed passwords and JWT/secure session cookies with HTTPS.
2. Integrate digital signature generation and PDF rendering for verified certificate downloads.
3. Integrate college LDAP / Single Sign-On (SSO) authentication.
