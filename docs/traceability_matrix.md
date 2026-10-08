# Requirements Traceability Matrix (RTM)
**Project Title:** Certificate Request System  
**Institution:** Sri Eshwar College of Engineering  
**Assessment:** Software Engineering SAT II Assessment  

---

| Requirement ID | Requirement Description | UML Element | Implementation Component | Test ID / Verification |
|---|---|---|---|---|
| **FR1** | Create and display certificate requests with unique ID and required service details. | `UC3: Create Certificate Request`<br>`ServiceRequest` class | `user_routes.py`<br>`RequestService.submit_request()`<br>`templates/create_request.html` | **T5**, `test_all_requirements.py` |
| **FR2** | Validate active-request limit (max 5) and user/service eligibility before submission. | `UC4: Validate Request`<br>`ValidationService.check_active_request_limit()` | `services/validation_service.py`<br>`RequestService.submit_request()` | **T2**, **T3**, **T7**, `test_br1_active_limit.py`, `test_br2_eligibility.py` |
| **FR3** | Display applicable charge, summary, and current request status. | `UC5: View Charge & Status`<br>`ValidationService.calculate_charge()` | `services/validation_service.py`<br>`static/js/app.js`<br>`templates/user_dashboard.html` | **T4**, `test_br4_charge.py` |
| **FR4** | Validate user, request details (name, 10-digit phone, reference) and current eligibility before submission. | `UC4: Validate Request`<br>`ValidationService.validate_details()` | `services/validation_service.py`<br>`routes/user_routes.py` | **T6**, `test_br5_validation.py` |
| **FR5** | Create unique `SUBMITTED` request, save master snapshot, allocate/reference resource, and record history atomically. | `UC3: Create Request`<br>`ServiceRequest`<br>`RequestStatusHistory` | `services/request_service.py`<br>`database/schema.sql`<br>`database/db.py` | **T5**, **T1**, `test_all_requirements.py`, `test_br6_no_partial_update.py` |
| **FR6** | Display logged-in user's own requests and detailed view. | `UC6: View Own Requests`<br>`UC7: View Request Details` | `routes/user_routes.py`<br>`templates/my_requests.html`<br>`templates/request_details.html` | **T8**, `test_br10_access.py` |
| **FR7** | Allow administrator to move request only to the next valid sequential status. | `UC10`, `UC11`, `UC12`<br>`ValidationService.validate_status_transition()` | `services/request_service.py`<br>`routes/admin_routes.py`<br>`templates/admin_dashboard.html` | **T9**, `test_br8_status.py` |
| **FR8** | Allow eligible cancellation of `SUBMITTED` request and release resource capacity exactly once. | `UC8: Cancel Submitted Request`<br>`RequestService.cancel_request()` | `services/request_service.py`<br>`routes/user_routes.py`<br>`templates/request_details.html` | **T10**, `test_br9_cancellation.py` |
| **FR9** | Show clear, user-friendly error messages for invalid input, unauthorized access, or invalid status change. | `ValidationError`<br>`templates/error.html` | `services/validation_service.py`<br>`routes/auth_routes.py`<br>`templates/base.html` | **T3**, **T6**, **T8**, **T9**, `test_br5_validation.py` |
| **FR10** | Store users, requests/resources, and status history in persistent SQLite database surviving restarts. | `database/schema.sql`<br>`database/db.py`<br>`config.py` | `database/db.py`<br>`seed.py`<br>`app.py` | **T11**, `test_all_requirements.py` |

---

### Business Rule Mapping Summary

| Business Rule | Rule Name | Enforcing Component | Automated Test Suite | Status |
|---|---|---|---|---|
| **BR1** | Active Request Limit (&le; 5) | `ValidationService.check_active_request_limit` | `tests/test_br1_active_limit.py` (T2) | **VERIFIED PASS** |
| **BR2** | Comprehensive Eligibility | `ValidationService.validate_eligibility` | `tests/test_br2_eligibility.py` (T3, T7) | **VERIFIED PASS** |
| **BR3** | Master Data Snapshot | `RequestService.submit_request` | `tests/test_br3_snapshot.py` (T12) | **VERIFIED PASS** |
| **BR4** | Statutory Fee / Charge | `ValidationService.calculate_charge` | `tests/test_br4_charge.py` (T4) | **VERIFIED PASS** |
| **BR5** | Details Validation | `ValidationService.validate_details` | `tests/test_br5_validation.py` (T6) | **VERIFIED PASS** |
| **BR6** | Submission Failure / Rollback | `RequestService.submit_request` | `tests/test_br6_no_partial_update.py` (T1, T6) | **VERIFIED PASS** |
| **BR7** | Atomic Success | `RequestService.submit_request` | `tests/test_all_requirements.py` (T5) | **VERIFIED PASS** |
| **BR8** | Sequential Status Flow | `ValidationService.validate_status_transition` | `tests/test_br8_status.py` (T9) | **VERIFIED PASS** |
| **BR9** | Cancellation & Quota Release | `RequestService.cancel_request` | `tests/test_br9_cancellation.py` (T10) | **VERIFIED PASS** |
| **BR10** | Strict Access Control | `user_required`, `admin_required`, ownership checks | `tests/test_br10_access.py` (T8) | **VERIFIED PASS** |
