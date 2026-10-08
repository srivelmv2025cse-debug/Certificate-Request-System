# Certificate Request System

**Institution:** Sri Eshwar College of Engineering  
**Course / Assessment:** Software Engineering SAT II Assessment  

---

## 1. Project Title & Description
The **Certificate Request System** is a complete, lightweight, robust, and demonstrable web application engineered for college students and faculty administrators. It streamlines the lifecycle of institutional certificate applications:
```
Create Certificate Request → Validate → Submit → View Request → Administrator Process → Complete
```
Also supports:
```
User Cancellation of eligible SUBMITTED requests (releasing reserved capacity exactly once).
```

---

## 2. Key Features
- **Role-Based Access Control:** Strict separation between `USER` (students) and `ADMINISTRATOR` (college office).
- **Active Request Quotas (BR1):** Enforces a hard limit of at most 5 active requests per user.
- **Immediate Eligibility Verification (BR2):** Rechecks user status and service availability before atomic acceptance.
- **Historical Snapshots (BR3):** Captures immutable copies of service name and parameters at the time of submission (verified by T12).
- **Statutory Fee Logic (BR4):** Automatic charge calculation (< Rs.1000 &rarr; Rs.50; &ge; Rs.1000 &rarr; Rs.0).
- **Atomic Transactions (BR6 & BR7):** Full rollback on any validation failure; zero partial database updates.
- **Enforced Status Progression (BR8):** `SUBMITTED` &rarr; `APPROVED/ASSIGNED` &rarr; `IN_PROGRESS` &rarr; `COMPLETED` without stage skipping.
- **Atomic User Cancellation (BR9):** Allows cancellation of `SUBMITTED` requests and prevents double resource release.
- **Audit History Trail:** Complete event history log for every state transition and actor.
- **Responsive Web UI:** Clean, modern, accessible design with color-coded status badges, live fee calculator, and one-click demo login helpers.

---

## 3. Technology Stack
- **Backend:** Python 3.14+ with Flask 3.0.3
- **Database:** SQLite 3 (Persistent relational file `database.db` with Foreign Keys enabled)
- **Frontend:** HTML5, Jinja2 Templates, Vanilla CSS3 (Custom design system), Vanilla JavaScript (No heavy frameworks)
- **Automated Testing:** `pytest 9.1.1`

---

## 4. Project Structure
```
certificate-request-system/
│
├── app.py                      # Application entry point and factory
├── config.py                   # Central configuration
├── requirements.txt            # Dependency specification
├── README.md                   # Complete documentation and user guide
├── seed.py                     # Idempotent database and demo seeder
├── database.db                 # Persistent SQLite database file
│
├── models/
│   ├── __init__.py
│   ├── user.py                 # User domain entity
│   ├── service_request.py      # Certificate request entity with snapshot fields
│   ├── resource.py             # Service quota resource entity
│   └── status_history.py       # Request audit history entity
│
├── services/
│   ├── __init__.py
│   ├── validation_service.py   # Business rule validations (BR1, BR2, BR4, BR5, BR8)
│   └── request_service.py      # Transactional workflows, atomic rollback, and quota locks
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py          # Login, logout, role redirects
│   ├── user_routes.py          # Dashboard, request creation, cancellation, personal list
│   └── admin_routes.py         # Administrator dashboard, status advancement, master editor
│
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite connection provider and schema runner
│   └── schema.sql              # Relational table definitions with constraints
│
├── templates/
│   ├── base.html               # College-branded header, navigation, and flash alerts
│   ├── login.html              # Login portal with demo account auto-fill cards
│   ├── user_dashboard.html     # Student dashboard with quota progress bar
│   ├── create_request.html     # Application form with live BR4 fee preview
│   ├── request_details.html    # Request details, BR3 snapshot banner, and history table
│   ├── my_requests.html        # Filtered table of user requests
│   ├── admin_dashboard.html    # College-wide requests table and valid action triggers
│   └── error.html              # Custom error page for 403, 404, and validation rejections
│
├── static/
│   ├── css/
│   │   └── style.css           # Premium, accessible styling tokens and responsive rules
│   └── js/
│       └── app.js              # Real-time fee preview, capacity check, and cancellation prompts
│
├── tests/
│   ├── conftest.py             # Pytest database fixtures and cleanup
│   ├── test_br1_active_limit.py        # T2: Active limit quota (4, 5, 6)
│   ├── test_br2_eligibility.py         # T3, T7: Inactive services and capacity exhaustion
│   ├── test_br3_snapshot.py            # T12: Master data change snapshot immutability
│   ├── test_br4_charge.py              # T4: Boundary fee tests (999, 1000, 1001)
│   ├── test_br5_validation.py          # T6: Name, 10-digit phone, and required field validation
│   ├── test_br6_no_partial_update.py   # T1, T6: Transaction rollback and duplicate tests
│   ├── test_br8_status.py              # T9: Valid transitions and stage skipping rejection
│   ├── test_br9_cancellation.py        # T10: Single quota restoration & repeated cancel error
│   ├── test_br10_access.py             # T8: Cross-user and unauthorized admin route access
│   └── test_all_requirements.py        # T5, T11: Atomic success and app restart persistence
│
├── docs/
│   ├── requirement_analysis.md # Software requirements specification
│   ├── use_case_diagram.md     # Mermaid Use Case Diagram and specifications
│   ├── class_diagram.md        # Mermaid Class Diagram with methods and multiplicities
│   ├── traceability_matrix.md  # Complete RTM mapping FR1-FR10 to code and tests
│   ├── test_cases.md           # T1 - T12 test cases with actual execution results
│   ├── defect_log.md           # Real defect logs and resolution history
│   └── ai_test_report.md       # AI testing report with verified pytest output
│
└── screenshots/
    └── README.md               # Viva demonstration screenshots guide
```

---

## 5. Demo Accounts & Credentials
Display cards are embedded directly on the login page for viva testing:

| Role | Username | Password | Status | Intended Use |
|---|---|---|---|---|
| **USER 1** | `user1` | `user123` | `ACTIVE` | Primary student testing (BR1, BR4, BR9) |
| **USER 2** | `user2` | `user123` | `ACTIVE` | Cross-user access control validation (BR10) |
| **ADMINISTRATOR** | `admin` | `admin123` | `ACTIVE` | Academic authority processing requests (BR8) |

---

## 6. Demonstration Master Resources & Pre-Seeded Requests
Configured in SQLite database:

| Resource ID | Service Name | Total Capacity | Initial Available | Status |
|---|---|---|---|---|
| **S101** | Certificate Request A | 10 | 7 | `ACTIVE` |
| **S102** | Certificate Request B | 5 | 3 | `ACTIVE` |
| **S103** | Certificate Request C | 0 | 0 | `INACTIVE` |

### Pre-Seeded Demonstration Requests (12 Complete Records)

| Reference ID | User Account | Service Resource | Declared Amount | Statutory Charge | Current Status | Demonstration Scenario / Viva Talking Point |
|---|---|---|---|---|---|---|
| `REQ-20261008-0001` | `user1` | S101 | Rs. 500.00 | **Rs. 50.00** | `SUBMITTED` | Ready to demonstrate **User Cancellation (BR9)** or **Admin Approval (BR8)** |
| `REQ-20261008-0002` | `user1` | S101 | Rs. 1200.00 | **Rs. 0.00** | `APPROVED/ASSIGNED` | Ready for Admin to click **Move to IN_PROGRESS** (BR8) |
| `REQ-20261008-0003` | `user1` | S102 | Rs. 800.00 | **Rs. 50.00** | `IN_PROGRESS` | Ready for Admin to click **Complete** (BR8) |
| `REQ-20261008-0004` | `user1` | S102 | Rs. 1500.00 | **Rs. 0.00** | `COMPLETED` | Proves completed requests do not count toward active quota (BR1) |
| `REQ-20261008-0005` | `user1` | S101 | Rs. 250.00 | **Rs. 50.00** | `CANCELLED` | Proves cancellation releases resource capacity exactly once (BR9) |
| `REQ-20261008-0012` | `user1` | S101 | Rs. 500.00 | **Rs. 50.00** | `COMPLETED` | Historical request displaying permanent snapshot immutability (BR3/T12) |
| `REQ-20261008-0006` | `user2` | S101 | Rs. 450.00 | **Rs. 50.00** | `SUBMITTED` | Proves user isolation; `user1` cannot see or cancel this request (BR10) |
| `REQ-20261008-0007` | `user2` | S101 | Rs. 1000.00 | **Rs. 0.00** | `APPROVED/ASSIGNED` | Boundary test proof: Amount &ge; 1000 has Rs. 0 charge (BR4/T4) |
| `REQ-20261008-0008` | `user2` | S102 | Rs. 750.00 | **Rs. 50.00** | `COMPLETED` | Industrial Internship NOC with full 4-stage audit history trail |
| `REQ-20261008-0009` | `user2` | S101 | Rs. 600.00 | **Rs. 50.00** | `CANCELLED` | Demonstrates cancellation idempotence; repeating cancel shows error |
| `REQ-20261008-0010` | `user2` | S101 | Rs. 1800.00 | **Rs. 0.00** | `IN_PROGRESS` | Fee Structure Certificate in processing stage |
| `REQ-20261008-0011` | `user2` | S102 | Rs. 300.00 | **Rs. 50.00** | `COMPLETED` | Anna University Zonal Sports Endorsement letter |

---

## 7. Business Rules Implemented
- **BR1 (Active Request Limit):** Maximum 5 active requests (`status NOT IN ('COMPLETED', 'CANCELLED')`). Sixth request rejected with: *"Active request limit exceeded. A user can have at most 5 active requests."*
- **BR2 (Eligibility):** Rechecks user account and service availability immediately before transaction commit.
- **BR3 (Master Snapshot):** Records `service_name_snapshot` and `service_value_snapshot`. Later edits to master resources do not modify historical requests (verified by T12).
- **BR4 (Statutory Charge):**
  - Amount < Rs.1000 &rarr; Charge = Rs.50.
  - Amount &ge; Rs.1000 &rarr; Charge = Rs.0.
  - Non-chargeable scenario &rarr; Charge = Rs.0.
- **BR5 (Field Validation):** Non-empty name, exactly 10-digit numeric phone, mandatory description and reference fields.
- **BR6 (Submission Failure):** Atomic transaction rollback upon any failure. No partial records created.
- **BR7 (Success Transaction):** Atomic execution of request insertion, snapshot recording, resource decrement, and status history entry.
- **BR8 (Status Transitions):** Only sequential progression: `SUBMITTED` &rarr; `APPROVED/ASSIGNED` &rarr; `IN_PROGRESS` &rarr; `COMPLETED`. Stage skipping is strictly rejected.
- **BR9 (Cancellation):** Users can cancel only their own `SUBMITTED` requests. Restores capacity exactly once. Repeated attempts return: *"Request has already been cancelled."*
- **BR10 (Access Control):** Strict isolation. Users view only their own records. Admin routes blocked to standard users with *"Access denied."* (HTTP 403).

---

## 8. Installation & Run Instructions

### Step 1: Open Terminal in Project Directory
```powershell
cd "c:\Users\srive\OneDrive\Desktop\SE project  sart 2\certificate-request-system"
```

### Step 2: (Optional) Create and Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Seed Database
```powershell
python seed.py
```

### Step 5: Start Web Application
```powershell
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 9. Running Automated Tests
Run the entire automated test suite (T1 - T12) using `pytest`:
```powershell
pytest -v
```

All 22 automated test functions will execute and pass:
```
============================= 22 passed in 1.81s ==============================
```

---

## 10. Sample Viva Demonstration Workflow

### Step 1: Login as Student (`user1`)
1. Click the **USER 1** pill on the login page (`user1` / `user123`).
2. Click **Sign In to Portal**.

### Step 2: Submit a Valid Request (Demonstrate BR4 & BR7)
1. Click **+ Create Certificate Request**.
2. Select **S101 - Certificate Request A**.
3. Fill details:
   - Requester Name: `Demo Student`
   - Contact Phone: `9876543210`
   - Purpose: `Certificate request for academic purpose`
   - Reference Details: `CERT-DEMO-001`
   - Declared Amount: `999`
4. Notice the dynamic charge calculation displays **Rs. 50.00**.
5. Click **Submit Certificate Request**.
6. View generated Request ID (e.g., `REQ-20261008-0001`) with status `SUBMITTED`.

### Step 3: Demonstrate BR3 Snapshot Immutability (T12)
1. Notice the snapshot banner displays Snapshotted Service Name: `Certificate Request A`.
2. Logout and login as `admin` (`admin` / `admin123`).
3. Under **Master Resource Catalog**, update `S101` name to `Modified Name Alpha`.
4. Return to the request details: the historical record still displays `Certificate Request A`.

### Step 4: Process Request via Administrator Dashboard (BR8 & T9)
1. On the Admin Dashboard, locate `REQ-20261008-0001`.
2. Click **Approve / Assign** &rarr; Status becomes `APPROVED/ASSIGNED`.
3. Click **Move to IN_PROGRESS** &rarr; Status becomes `IN_PROGRESS`.
4. Click **Complete** &rarr; Status becomes `COMPLETED`.
5. Open details: full chronological history with timestamps is displayed.

### Step 5: Demonstrate User Cancellation & Quota Restoration (BR9 & T10)
1. Login back as `user1`.
2. Create another request for `S101`.
3. In **My Requests**, click **Cancel Request**.
4. Confirm cancellation: Status changes to `CANCELLED`, and `S101` available capacity increases by 1.
5. Attempting to cancel again is blocked with *"Request has already been cancelled."*

---

## 11. Limitations & Viva Notes
- Designed specifically as an educational Software Engineering prototype.
- Plain-text passwords are used for immediate demonstration ease without crypto dependencies.
- No third-party network or payment gateways are needed—runs 100% locally.
