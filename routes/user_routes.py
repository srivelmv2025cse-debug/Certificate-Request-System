from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from database.db import get_db_connection
from services.request_service import RequestService
from services.validation_service import ValidationService, ValidationError
from config import Config

user_bp = Blueprint("user", __name__, url_prefix="/user")

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "USER":
            return render_template("error.html", message="Access denied.", code=403), 403
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route("/dashboard")
@user_required
def user_dashboard():
    user_id = session["user_id"]
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Active request count
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM service_requests
            WHERE user_id = ? AND status NOT IN ('COMPLETED', 'CANCELLED')
            """,
            (user_id,)
        )
        active_count = cursor.fetchone()["count"]

        # Status summary counts
        cursor.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM service_requests
            WHERE user_id = ?
            GROUP BY status
            """,
            (user_id,)
        )
        status_rows = cursor.fetchall()
        summary = {
            "SUBMITTED": 0,
            "APPROVED/ASSIGNED": 0,
            "IN_PROGRESS": 0,
            "COMPLETED": 0,
            "CANCELLED": 0
        }
        for row in status_rows:
            if row["status"] in summary:
                summary[row["status"]] = row["count"]

        return render_template(
            "user_dashboard.html",
            user_name=session.get("name"),
            username=session.get("username"),
            role=session.get("role"),
            active_count=active_count,
            max_active=Config.MAX_ACTIVE_REQUESTS,
            summary=summary
        )
    finally:
        conn.close()

@user_bp.route("/create-request", methods=["GET", "POST"])
@user_required
def create_request():
    user_id = session["user_id"]
    resources = RequestService.get_all_resources()

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM service_requests
            WHERE user_id = ? AND status NOT IN ('COMPLETED', 'CANCELLED')
            """,
            (user_id,)
        )
        active_count = cursor.fetchone()["count"]
    finally:
        conn.close()

    if request.method == "POST":
        service_id = request.form.get("service_id", "").strip()
        requester_name = request.form.get("requester_name", "").strip()
        phone = request.form.get("phone", "").strip()
        description = request.form.get("description", "").strip()
        reference_details = request.form.get("reference_details", "").strip()
        amount_raw = request.form.get("chargeable_amount", "0").strip()

        try:
            amount = float(amount_raw) if amount_raw else 0.0
            new_req = RequestService.submit_request(
                user_id=user_id,
                service_id=service_id,
                requester_name=requester_name,
                phone=phone,
                description=description,
                reference_details=reference_details,
                chargeable_amount=amount
            )
            flash(f"Certificate request submitted successfully. Request ID: {new_req.reference_id}", "success")
            return redirect(url_for("user.request_details", reference_id=new_req.reference_id))

        except ValidationError as e:
            flash(str(e.message), "error")
            return render_template(
                "create_request.html",
                resources=resources,
                active_count=active_count,
                max_active=Config.MAX_ACTIVE_REQUESTS,
                form_data=request.form
            )
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", "error")
            return render_template(
                "create_request.html",
                resources=resources,
                active_count=active_count,
                max_active=Config.MAX_ACTIVE_REQUESTS,
                form_data=request.form
            )

    return render_template(
        "create_request.html",
        resources=resources,
        active_count=active_count,
        max_active=Config.MAX_ACTIVE_REQUESTS,
        form_data={}
    )

@user_bp.route("/requests")
@user_required
def my_requests():
    user_id = session["user_id"]
    requests = RequestService.get_user_requests(user_id)
    return render_template("my_requests.html", requests=requests)

@user_bp.route("/requests/<reference_id>")
@user_required
def request_details(reference_id):
    user_id = session["user_id"]
    req = RequestService.get_request_by_reference(reference_id)
    if not req:
        return render_template("error.html", message="Request not found.", code=404), 404

    # BR10: User can view only their own requests
    if req.user_id != user_id:
        return render_template("error.html", message="Access denied.", code=403), 403

    history = RequestService.get_request_history(reference_id)
    resource = RequestService.get_resource(req.resource_id)

    return render_template(
        "request_details.html",
        req=req,
        history=history,
        resource=resource
    )

@user_bp.route("/requests/<reference_id>/cancel", methods=["POST"])
@user_required
def cancel_request(reference_id):
    user_id = session["user_id"]
    req = RequestService.get_request_by_reference(reference_id)
    if not req:
        return render_template("error.html", message="Request not found.", code=404), 404

    # BR10: Check ownership
    if req.user_id != user_id:
        return render_template("error.html", message="Access denied.", code=403), 403

    try:
        RequestService.cancel_request(reference_id, user_id)
        flash("Certificate request cancelled successfully. Resource has been released.", "success")
    except ValidationError as e:
        flash(str(e.message), "error")

    return redirect(url_for("user.request_details", reference_id=reference_id))
