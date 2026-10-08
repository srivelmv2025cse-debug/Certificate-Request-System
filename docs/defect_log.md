# Defect Log Document
**Project Title:** Certificate Request System  
**Institution:** Sri Eshwar College of Engineering  
**Assessment:** Software Engineering SAT II Assessment  

---

## Defect Tracking Log

| Defect ID | Description | Impact | Root Cause | Fix | Retest | Status |
|---|---|---|---|---|---|---|
| **DEF-001** | Windows file lock (`WinError 32 PermissionError`) during temporary test database teardown in pytest. | Test suite execution flagged teardown warning on Windows OS when deleting temp SQLite database file. | SQLite connections created inside test verification assertions were not explicitly closed before pytest fixture removal, leaving open OS file handles on Windows. | Explicitly closed all open SQLite connection instances across test functions and wrapped fixture cleanup with `gc.collect()` and defensive exception handling. | Re-executed `pytest -v`. All 22 test items passed cleanly in 1.81s with 0 errors. | **CLOSED** |

---

### Verification Summary
- **Open Defects:** 0
- **Closed Defects:** 1
- **Current System Quality:** Stable, fully verified against all functional requirements FR1-FR10 and business rules BR1-BR10.
