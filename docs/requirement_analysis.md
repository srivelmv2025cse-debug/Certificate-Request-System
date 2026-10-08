# Requirement Analysis Document
**Project Title:** Certificate Request System  
**Institution:** Sri Eshwar College of Engineering  
**Assessment:** Software Engineering SAT II Assessment  

---

## 1. Project Title
**Certificate Request System** (SE Project SAT II)

## 2. Problem Summary
In educational institutions like Sri Eshwar College of Engineering, students regularly request bona fide certificates, conduct certificates, course completion letters, and academic verification documents. Manual and ad-hoc processing often leads to unverified requests, lost records, quota violations, and lack of transparency regarding processing stages and fee calculations. 

The **Certificate Request System** provides an automated, reliable, and auditable digital workflow allowing students to apply for designated certificate types, calculate statutory charges automatically based on declared threshold amounts, maintain strict active request quotas, and enable administrative staff to process applications through non-skippable verification stages with full transaction atomicity.

## 3. Scope
- Scope includes two system actors: **USER** (students/requesters) and **ADMINISTRATOR** (academic authority/office).
- Automated submission workflow: Create &rarr; Validate &rarr; Submit &rarr; View &rarr; Admin Process (Approve &rarr; In Progress &rarr; Complete).
- Eligible user cancellation of submitted requests with immediate resource quota restoration.
- Single persistent SQLite database surviving application restarts.
- Strict rejection of unauthorized access, status skipping, and double resource releases.
- Excluded: Third-party payment gateways, external cloud dependencies, biometric logins, or complex microservices.

## 4. Actors
1. **USER**: Enrolled student who signs in, browses available certificate services, submits valid applications, monitors application stages, and cancels pending submitted requests.
2. **ADMINISTRATOR**: Authorized college administrator who reviews all student requests across the college, moves requests sequentially through approved lifecycle states, and manages service capacities.

## 5. Functional Requirements (FR1 - FR10)
- **FR1:** Create and display certificate requests with a unique reference ID (e.g., `REQ-YYYYMMDD-XXXX`) and required service parameters.
- **FR2:** Validate user eligibility and active-request limit (at most 5 active requests).
- **FR3:** Automatically calculate and display applicable charges, application summary, and real-time status.
- **FR4:** Validate user account status, phone format, requester name, and service resource availability before submission.
- **FR5:** Atomically create `SUBMITTED` request, capture immutable service snapshots, decrement available resource capacity, and write initial status history.
- **FR6:** Allow logged-in users to view only their own requests, snapshots, and progress logs.
- **FR7:** Enable administrators to view all requests and advance requests strictly to the next valid lifecycle stage.
- **FR8:** Allow eligible users to cancel their own `SUBMITTED` request, restoring allocated resource capacity exactly once.
- **FR9:** Provide explicit, user-friendly error notifications for invalid input, unauthorized cross-user access, or invalid status progressions.
- **FR10:** Persistently store users, requests, resources, and status history logs in an SQLite relational database.

## 6. Non-Functional Requirements (NFRs)
- **NFR1 (Reliability):** Strict transaction atomicity using database transactions (`BEGIN` ... `COMMIT` / `ROLLBACK`). No partial updates occur if any validation or allocation step fails.
- **NFR2 (Persistence):** Data survives server restarts and power cycles without data loss or corruption.
- **NFR3 (Maintainability):** Three-tier layered architecture separating Presentation (Jinja2/HTML5/CSS), Business Logic (Validation & Request Services), and Data Persistence (SQLite/Models).
- **NFR4 (Usability):** Intuitive responsive user interface with clear status badges, color semantics (Blue, Green, Orange, Red, Gray), and unambiguous validation prompts.
- **NFR5 (Security Design):** Session-based authentication, role-based authorization guards, strict request ownership verification, and parameterized SQL queries preventing SQL injection.

## 7. Business Rules (BR1 - BR10)
- **BR1 (Active Request Limit):** A user may have at most 5 active requests (requests that are not `COMPLETED` or `CANCELLED`). A 6th active request must be rejected with: *"Active request limit exceeded. A user can have at most 5 active requests."*
- **BR2 (Eligibility):** A certificate request can be submitted only when: (1) User is `ACTIVE`, (2) Service/Resource is `ACTIVE`, (3) User active quota is available, and (4) Available capacity > 0. Recheck eligibility immediately before acceptance.
- **BR3 (Snapshot):** At submission time, snapshot `service_name_snapshot` and `service_value_snapshot`. Future edits to master service records must never alter historical requests.
- **BR4 (Charge Calculation):**
  - Amount < Rs.1000 &rarr; Charge = Rs.50.
  - Amount &ge; Rs.1000 &rarr; Charge = Rs.0.
  - Non-chargeable scenario &rarr; Charge = Rs.0.
- **BR5 (Details Validation):** Requester Name cannot be blank; Phone must be exactly 10 numeric digits; Description and Reference Details cannot be blank.
- **BR6 (Submission Failure):** Any validation failure causes immediate atomic rollback. No request, no resource decrement, and no history entry are committed.
- **BR7 (Atomic Success):** On successful validation: create `SUBMITTED` request, save snapshot, reserve resource, and insert history together in a single transaction.
- **BR8 (Status Flow):** Only sequential progression is allowed: `SUBMITTED` &rarr; `APPROVED/ASSIGNED` &rarr; `IN_PROGRESS` &rarr; `COMPLETED`. Stage skipping is strictly rejected.
- **BR9 (Cancellation):** Users can cancel only their own `SUBMITTED` requests (`SUBMITTED` &rarr; `CANCELLED`). The reserved capacity is released exactly once. Repeated cancellation is rejected with: *"Request has already been cancelled."*
- **BR10 (Access Control):** Users can only access their own records and cannot perform admin transitions. Administrators can view all records and process statuses. Unauthorized attempts return *"Access denied."*

## 8. Assumptions
- Student users and administrator credentials are created by institutional authorities.
- Charges represent processing administrative fees determined by declared base amounts.
- Requests operate on local academic server environments without external cloud services.

## 9. Constraints
- Technology stack: Python 3.x, Flask, SQLite3, Jinja2, Vanilla CSS.
- Exactly two actors: USER and ADMINISTRATOR.
- No external payment gateway or external API dependencies.

## 10. System Workflow
```
[User Login] 
     ↓
[Select Active Service (S101/S102)]
     ↓
[Enter Details & Fee Base] → [Live BR4 Charge Preview]
     ↓
[Submit Request]
     ↓
[Server Validation & BR1/BR2/BR5 Recheck]
     ↓ (Success)
[Atomic DB Transaction: Insert Request + Snapshot BR3 + Decrement Quota + Insert History]
     ↓
[Status: SUBMITTED]
     ├── User Option: [Cancel Request] → Status: CANCELLED (Restore Quota Once)
     └── Admin Workflow:
             ↓
         [Approve / Assign] → Status: APPROVED/ASSIGNED
             ↓
         [Move to In Progress] → Status: IN_PROGRESS
             ↓
         [Complete] → Status: COMPLETED
```

## 11. Traceability Summary
All functional requirements FR1-FR10 and business rules BR1-BR10 map directly to database schema elements, service methods, web endpoints, and automated tests T1-T12, documented in `traceability_matrix.md`.
