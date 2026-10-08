# UML Diagram 2: Class Diagram
**Project Title:** Certificate Request System  
**Institution:** Sri Eshwar College of Engineering  

---

## 1. Description
The Class Diagram illustrates the structural architecture of the **Certificate Request System**, showcasing domain entities (`User`, `Resource`, `ServiceRequest`, `RequestStatusHistory`), service managers (`ValidationService`, `RequestService`), their public operations, private attributes, multiplicities, and relationships.

---

## 2. Mermaid Class Diagram

```mermaid
classDiagram
    %% Entities
    class User {
        +int id
        +string name
        +string username
        +string password
        +string role
        +string status
        +datetime created_at
        +from_row(row) User
        +is_active() bool
        +is_admin() bool
    }

    class Resource {
        +int id
        +string resource_id
        +string service_name
        +int capacity
        +int available_capacity
        +string status
        +int owner_user_id
        +datetime created_at
        +from_row(row) Resource
        +is_available() bool
    }

    class ServiceRequest {
        +int id
        +string reference_id
        +int user_id
        +string service_id
        +string service_name_snapshot
        +float service_value_snapshot
        +string requester_name
        +string phone
        +string description
        +string reference_details
        +float charge
        +string status
        +string resource_id
        +datetime created_at
        +datetime updated_at
        +datetime cancelled_at
        +from_row(row) ServiceRequest
    }

    class RequestStatusHistory {
        +int id
        +string reference_id
        +int actor_id
        +string old_status
        +string new_status
        +datetime event_at
        +from_row(row) RequestStatusHistory
    }

    %% Service Layers
    class ValidationService {
        +dict STATUS_TRANSITION_MAP
        +validate_user(user) bool
        +validate_service(service_resource) bool
        +validate_details(requester_name, phone, description, reference_details) bool
        +check_active_request_limit(user_id, conn) int
        +calculate_charge(amount) float
        +validate_eligibility(user_id, service_id, conn) tuple
        +validate_status_transition(current_status, next_status) bool
    }

    class RequestService {
        +generate_reference_id(conn) string
        +submit_request(user_id, service_id, requester_name, phone, description, reference_details, amount, db_path) ServiceRequest
        +get_request_by_reference(reference_id, conn) ServiceRequest
        +get_user_requests(user_id, conn) List~ServiceRequest~
        +get_all_requests(conn) List~ServiceRequest~
        +get_request_history(reference_id, conn) List~RequestStatusHistory~
        +cancel_request(reference_id, user_id, db_path) bool
        +advance_status(reference_id, next_status, admin_user, db_path) bool
        +get_resource(resource_id, conn) Resource
        +get_all_resources(conn) List~Resource~
    }

    %% Relationships and Multiplicities
    User "1" -- "0..*" ServiceRequest : submits >
    User "1" -- "0..*" Resource : owns/manages >
    User "1" -- "0..*" RequestStatusHistory : triggers >
    Resource "1" -- "0..*" ServiceRequest : allocated_to >
    ServiceRequest "1" -- "1..*" RequestStatusHistory : audits >

    RequestService ..> ServiceRequest : creates/updates
    RequestService ..> Resource : allocates/releases
    RequestService ..> RequestStatusHistory : logs
    RequestService ..> ValidationService : invokes validation rules
```

---

## 3. Structural Multiplicities & Responsibilities

1. **User (1) to ServiceRequest (0..\*):**
   - Each registered student (`User`) can submit 0 or more certificate requests.
   - Enforced by `BR1`: A user can have at most 5 concurrently active requests.
2. **Resource (1) to ServiceRequest (0..\*):**
   - Each master catalog item (`Resource`: S101, S102, S103) is linked to zero or more submitted requests.
   - Allocating a request decrements `available_capacity` by 1; cancelling releases it by 1 (`BR9`).
3. **ServiceRequest (1) to RequestStatusHistory (1..\*):**
   - Every service request has at least one audit record (`SUBMITTED`), plus sequential logs for each stage advance (`APPROVED/ASSIGNED`, `IN_PROGRESS`, `COMPLETED`) or cancellation (`CANCELLED`).
4. **ValidationService:**
   - Central stateless service encapsulating business rules `BR1` (active limit), `BR2` (eligibility), `BR4` (charge calculation), `BR5` (field format validation), and `BR8` (status transition map).
5. **RequestService:**
   - Transactional service handling atomic request submissions (`BR6`, `BR7`), snapshots (`BR3`), resource quota locks, and role checks (`BR10`).
