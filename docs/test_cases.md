# Test Cases Specification & Results Document
**Project Title:** Certificate Request System  
**Institution:** Sri Eshwar College of Engineering  
**Assessment:** Software Engineering SAT II Assessment  

---

### Test Suite Execution Summary
- **Total Test Cases Executed:** 12 mandatory specification tests (T1 - T12) across 22 automated test methods.
- **Pass Count:** 22 / 22 (100% Passed)
- **Fail Count:** 0
- **Test Framework:** `pytest 9.1.1` on Python 3.14.3 (Windows environment)

---

## Detailed Test Cases (T1 - T12)

### Test ID: T1
- **Linked FR:** FR1, FR5
- **Linked BR:** BR6, BR7
- **Precondition:** User `user1` is active; resource `S101` has available capacity = 10.
- **Input:** Submit the same certificate request form parameters twice consecutively.
- **Expected Result:** Both requests generate distinct, unique IDs (e.g. `REQ-20261008-0001` and `REQ-20261008-0002`); capacity decremented by exactly 2; no duplicate IDs or data corruption.
- **Actual Result:** Distinct unique reference IDs generated; capacity updated from 10 to 8; zero duplicates.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/01_t1_duplicate_submission.png` (Automated: `tests/test_br6_no_partial_update.py::test_t1_no_duplicate_incorrect_records`)

---

### Test ID: T2
- **Linked FR:** FR2
- **Linked BR:** BR1
- **Precondition:** User `user1` is active and has 0 active requests initially.
- **Input:** Submit requests sequentially for counts 4, 5, and 6.
- **Expected Result:** Request 4 accepted. Request 5 accepted. Request 6 rejected with: *"Active request limit exceeded. A user can have at most 5 active requests."* No database state changes after rejection.
- **Actual Result:** Requests 1-5 accepted. 6th submission raises `ValidationError` with exact message; database state remains unchanged at 5 records.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/02_t2_active_limit_quota.png` (Automated: `tests/test_br1_active_limit.py::test_t2_active_request_limit_4_5_6`)

---

### Test ID: T3
- **Linked FR:** FR2, FR4
- **Linked BR:** BR2
- **Precondition:** Resource `S103` is configured in database with status `INACTIVE` and capacity = 0.
- **Input:** Submit certificate request choosing service `S103`.
- **Expected Result:** Request rejected with error: *"The selected service is inactive."* Database state and resource records remain unchanged.
- **Actual Result:** Request rejected immediately; exact message displayed; zero records inserted.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/03_t3_inactive_service.png` (Automated: `tests/test_br2_eligibility.py::test_t3_inactive_service_s103`)

---

### Test ID: T4
- **Linked FR:** FR3
- **Linked BR:** BR4
- **Precondition:** Validation service charge calculator active.
- **Input:** Test amounts: Rs.999, Rs.1000, and Rs.1001.
- **Expected Result:**
  - Rs.999 &rarr; Charge = Rs.50.00
  - Rs.1000 &rarr; Charge = Rs.0.00 (Waived)
  - Rs.1001 &rarr; Charge = Rs.0.00 (Waived)
- **Actual Result:** `calculate_charge(999)` returns `50.0`; `calculate_charge(1000)` returns `0.0`; `calculate_charge(1001)` returns `0.0`.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/04_t4_charge_boundary.png` (Automated: `tests/test_br4_charge.py::test_t4_charge_boundary_values`)

---

### Test ID: T5
- **Linked FR:** FR1, FR3, FR4, FR5
- **Linked BR:** BR7
- **Precondition:** User `user1` is active, service `S101` has capacity 10.
- **Input:** Name: "Demo Student", Phone: "9876543210", Description: "Academic bona fide", Reference: "CERT-DEMO-001", Amount: 999.
- **Expected Result:** Request created with status `SUBMITTED`, charge = Rs.50, snapshot values saved, available capacity decremented to 9, initial status history recorded atomically.
- **Actual Result:** All 4 steps succeed atomically within a single transaction; record verified in database.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/05_t5_valid_submission.png` (Automated: `tests/test_all_requirements.py::test_t5_complete_valid_submission_atomic_success`)

---

### Test ID: T6
- **Linked FR:** FR4, FR9
- **Linked BR:** BR5, BR6
- **Precondition:** Valid logged-in user.
- **Input:** Submissions with: (a) blank name, (b) phone="123", (c) phone with alphabets, (d) empty description.
- **Expected Result:** Rejected with corresponding validation messages: *"Name cannot be blank."*, *"Phone number must contain exactly 10 digits."*, *"Description cannot be blank."* No partial updates.
- **Actual Result:** All invalid variations rejected with exact messages; resource capacities remain untouched.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/06_t6_details_validation.png` (Automated: `tests/test_br5_validation.py`)

---

### Test ID: T7
- **Linked FR:** FR2, FR4
- **Linked BR:** BR2, BR6
- **Precondition:** User begins request, but service capacity is exhausted to 0 right before acceptance.
- **Input:** Submit request for service with 0 remaining capacity.
- **Expected Result:** Request rejected with: *"The selected service/resource is currently unavailable."* No partial update.
- **Actual Result:** Recheck immediately catches exhaustion, rejects request, rollback confirmed.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/07_t7_resource_exhaustion.png` (Automated: `tests/test_br2_eligibility.py::test_t7_change_eligibility_resource_before_acceptance`)

---

### Test ID: T8
- **Linked FR:** FR6, FR9
- **Linked BR:** BR10
- **Precondition:** User `user1` owns a submitted request; User `user2` is logged in.
- **Input:** User `user2` attempts to view `/user/requests/<user1_ref>` or send cancellation POST.
- **Expected Result:** Access denied with error: *"Access denied."* HTTP 403 returned; no data change. User also denied admin routes.
- **Actual Result:** Returns HTTP 403 / *"Access denied."* Database record remains untouched.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/08_t8_access_control.png` (Automated: `tests/test_br10_access.py`)

---

### Test ID: T9
- **Linked FR:** FR7
- **Linked BR:** BR8
- **Precondition:** Administrator logged in with request in `SUBMITTED` status.
- **Input:** (a) Attempt `SUBMITTED` &rarr; `IN_PROGRESS` or `COMPLETED`. (b) Advance `SUBMITTED` &rarr; `APPROVED/ASSIGNED` &rarr; `IN_PROGRESS` &rarr; `COMPLETED`.
- **Expected Result:** Invalid stage skipping rejected with *"Invalid status transition."* Sequential progression succeeds at every step.
- **Actual Result:** Stage skips rejected; valid sequential progression completes successfully; all history recorded.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/09_t9_status_flow.png` (Automated: `tests/test_br8_status.py`)

---

### Test ID: T10
- **Linked FR:** FR8
- **Linked BR:** BR9
- **Precondition:** User `user1` has a `SUBMITTED` request; resource `S101` capacity was decremented.
- **Input:** (a) Submit cancellation request. (b) Submit repeated cancellation request on same ID.
- **Expected Result:** First cancellation updates status to `CANCELLED` and increments capacity by 1. Repeated cancellation rejected with: *"Request has already been cancelled."* Capacity not changed twice.
- **Actual Result:** First cancellation releases resource once; second cancellation raises `ValidationError` with exact message; capacity remains stable.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/10_t10_cancellation_idempotence.png` (Automated: `tests/test_br9_cancellation.py`)

---

### Test ID: T11
- **Linked FR:** FR10
- **Linked BR:** BR7
- **Precondition:** Application is running with SQLite database.
- **Input:** Submit request, terminate application, restart application with a fresh database connection, inspect data.
- **Expected Result:** Request, status, snapshot, and quota values persist exactly as stored.
- **Actual Result:** All tables, foreign keys, and records survive restart seamlessly.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/11_t11_restart_persistence.png` (Automated: `tests/test_all_requirements.py::test_t11_database_persistence_after_application_restart`)

---

### Test ID: T12
- **Linked FR:** FR1, FR5
- **Linked BR:** BR3
- **Precondition:** Request submitted under master service `S101` ("Certificate Request A", capacity 10).
- **Input:** Administrator alters master record of `S101` to "MODIFIED Certificate Request Alpha" and capacity 999.
- **Expected Result:** Historical request keeps original snapshot values (`service_name_snapshot` = "Certificate Request A", `service_value_snapshot` = 10.0).
- **Actual Result:** Historical request retains original values; master updates do not affect historical record.
- **Pass/Fail:** **PASS**
- **Evidence / Screenshot:** `screenshots/12_t12_snapshot_immutability.png` (Automated: `tests/test_br3_snapshot.py`)
