from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db_connection
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "ADMINISTRATOR":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("user.user_dashboard"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()

            if not user_row or user_row["password"] != password:
                flash("Invalid username or password.", "error")
                return render_template("login.html")

            user = User.from_row(user_row)
            if not user.is_active():
                flash("User account is inactive. Please contact administrator.", "error")
                return render_template("login.html")

            # Set session
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["name"] = user.name
            session["role"] = user.role

            flash(f"Welcome back, {user.name}!", "success")
            if user.is_admin():
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("user.user_dashboard"))
        finally:
            conn.close()

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
