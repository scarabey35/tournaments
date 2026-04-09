from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        if User.query.filter_by(email=email).first():
            flash("Email вже використовується", "danger")
            return redirect(url_for("user.register"))

        user = User(
            name=request.form.get("name"),
            email=email,
            password_hash=generate_password_hash(request.form.get("password")),
            role=request.form.get("role", "team")
        )
        db.session.add(user)
        db.session.commit()

        flash("Реєстрація успішна! Тепер увійдіть.", "success")
        return redirect(url_for("user.login"))

    return render_template("register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Вхід виконано успішно!", "success")
            return redirect(url_for("user.profile"))

        flash("Невірний email або пароль", "danger")

    return render_template("login.html")


@user_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("landing.landing"))


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # логіка зміни пароля
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        if not check_password_hash(current_user.password_hash, old_password):
            flash("Старий пароль невірний", "danger")
            return redirect(url_for("user.profile"))

        if new_password != confirm:
            flash("Паролі не співпадають", "danger")
            return redirect(url_for("user.profile"))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Пароль успішно змінено!", "success")

    return render_template("profile.html", user=current_user)
