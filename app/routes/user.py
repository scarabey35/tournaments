from flask import Blueprint, request, redirect, url_for, flash, render_template, get_flashed_messages, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, User, Team

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("landing.home"))

    if request.method == "GET":
        get_flashed_messages()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "team")

        if not name or not email or not password:
            flash("Усі поля обовʼязкові для заповнення", "danger")
            return redirect(url_for("user.register"))

        if len(name) < 4:
            flash("Ім'я користувача має містити мінімум 4 символи", "danger")
            return redirect(url_for("user.register"))

        if len(password) < 8:
            flash("Пароль має містити мінімум 8 символів", "danger")
            return redirect(url_for("user.register"))

        if User.query.filter_by(email=email).first():
            flash("Email вже використовується", "danger")
            return redirect(url_for("user.register"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Реєстрація успішна!", "success")

        return redirect(url_for("landing.home"))

    return render_template("register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Вхід виконано успішно!", "success")

            return redirect(url_for("landing.home"))
        flash("Невірний email або пароль", "danger")

    return render_template("login.html")


@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("landing.landing"))


@user_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    # Team data for role=team
    team = None
    if current_user.role == "team" and current_user.team_id:
        team = Team.query.get(current_user.team_id)

    # Jury data: list of evaluated submissions
    jury_evaluations = []
    if current_user.role == "jury":
        from app.models import Evaluation
        jury_evaluations = (
            Evaluation.query
            .filter_by(jury_id=current_user.id)
            .all()
        )

    return render_template(
        "profile.html",
        user=current_user,
        team=team,
        jury_evaluations=jury_evaluations,
    )


@user_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not old_password or not new_password or not confirm_password:
        flash("Fill in all fields to change password", "danger")
        return redirect(url_for("user.profile"))

    if not check_password_hash(current_user.password_hash, old_password):
        flash("Current password is incorrect", "danger")
        return redirect(url_for("user.profile"))

    if new_password != confirm_password:
        flash("New password and confirmation do not match", "danger")
        return redirect(url_for("user.profile"))

    if old_password == new_password:
        flash("New password must be different from current password", "danger")
        return redirect(url_for("user.profile"))

    if len(new_password) < 8:
        flash("New password must be at least 8 characters long", "danger")
        return redirect(url_for("user.profile"))

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash("Password changed successfully", "success")
    return redirect(url_for("user.profile"))


@user_bp.route("/settings")
def settings():
    return render_template("settings.html")
