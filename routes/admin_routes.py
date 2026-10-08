from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db_connection
from models.user import User
from services.request_service import RequestService
from services.validation_service import ValidationError

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "ADMINISTRATOR":
            return render_template("error.html", message="Access denied.", code=403), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    requests = RequestService.get_all_requests()
    resources = RequestService.get_all_resources()

    # Pre-calculate summary metrics
    summary = {
        "TOTAL": len(requests),
        "SUBMITTED": sum(1 for r in requests if r["status"] == "SUBMITTED"),
        "APPROVED": sum(1 for r in requests if r["status"] == "APPROVED/ASSIGNED"),
        "IN_PROGRESS": sum(1 for r in requests if r["status"] == "IN_PROGRESS"),
        "COMPLETED": sum(1 for r in requests if r["status"] == "COMPLETED"),
        "CANCELLED": sum(1 for r in requests if r["status"] == "CANCELLED"),
    }

    return render_template(
        "admin_dashboard.html",
        admin_name=session.get("name"),
        requests=requests,
        resources=resources,
        summary=summary
    )

@admin_bp.route("/requests/<reference_id>")
@admin_required
def request_details(reference_id):
    req = RequestService.get_request_by_reference(reference_id)
    if not req:
        return render_template("error.html", message="Request not found.", code=404), 404

    history = RequestService.get_request_history(reference_id)
    resource = RequestService.get_resource(req.resource_id)

    return render_template(
        "request_details.html",
        req=req,
        history=history,
        resource=resource,
        is_admin_view=True
    )

@admin_bp.route("/requests/<reference_id>/status", methods=["POST"])
@admin_required
def update_status(reference_id):
    next_status = request.form.get("next_status", "").strip()
    user = User(
        id=session.get("user_id"),
        name=session.get("name"),
        username=session.get("username"),
        role=session.get("role")
    )

    try:
        RequestService.advance_status(reference_id, next_status, user)
        flash(f"Request {reference_id} status updated to {next_status}.", "success")
    except ValidationError as e:
        flash(str(e.message), "error")
    except Exception as e:
        flash(f"Failed to update status: {str(e)}", "error")

    # If redirected from detail view, go there, else dashboard
    redirect_target = request.form.get("redirect_to", "dashboard")
    if redirect_target == "details":
        return redirect(url_for("admin.request_details", reference_id=reference_id))
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/resources/<resource_id>/edit", methods=["POST"])
@admin_required
def edit_resource(resource_id):
    """
    Demonstration helper: Update master service data to verify snapshot immutability (T12).
    """
    new_name = request.form.get("service_name", "").strip()
    new_capacity = request.form.get("capacity", "").strip()
    new_status = request.form.get("status", "ACTIVE").strip()

    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                UPDATE resources
                SET service_name = ?, capacity = ?, status = ?
                WHERE resource_id = ?
                """,
                (new_name, int(new_capacity), new_status, resource_id)
            )
        flash(f"Resource {resource_id} master record updated successfully.", "info")
    except Exception as e:
        flash(f"Failed to update resource: {str(e)}", "error")
    finally:
        conn.close()

    return redirect(url_for("admin.admin_dashboard"))
