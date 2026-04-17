from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask import get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
import re

user_bp = Blueprint("user", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def normalize_name(name: str) -> str:
    return " ".join((name or "").strip().split())


def validate_registration_data(name: str, email: str, password: str):
    errors = []

    if not name:
        errors.append("Ім'я є обов'язковим")
    elif len(name) < 2:
        errors.append("Ім'я має містити щонайменше 2 символи")
    elif len(name) > 255:
        errors.append("Ім'я не повинно перевищувати 255 символів")

    if not email:
        errors.append("Email є обов'язковим")
    elif len(email) > 255:
        errors.append("Email не повинен перевищувати 255 символів")
    elif not EMAIL_REGEX.match(email):
        errors.append("Введіть коректний email")

    if not password:
        errors.append("Пароль є обов'язковим")
    elif len(password) < 8:
        errors.append("Пароль має містити щонайменше 8 символів")
    elif len(password) > 128:
        errors.append("Пароль не повинен перевищувати 128 символів")

    return errors


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("landing.home"))

    if request.method == "GET":
        get_flashed_messages()

    if request.method == "POST":
        name = normalize_name(request.form.get("name"))
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password", "")

        errors = validate_registration_data(name, email, password)

        if User.query.filter_by(email=email).first():
            errors.append("Email вже використовується")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", form_data={"name": name, "email": email}), 400

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="team",
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Реєстрація успішна!", "success")
	
        return redirect(url_for("landing.home"))

    return render_template("register.html", form_data={"name": "", "email": ""})


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("landing.home"))

    if request.method == "GET":
        get_flashed_messages()

    if request.method == "POST":
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password", "")

        if not email or not password:
            flash("Введіть email і пароль", "danger")
            return render_template("login.html"), 400

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Вхід виконано успішно!", "success")
            return redirect(url_for("landing.home"))

        flash("Невірний email або пароль", "danger")
        return render_template("login.html"), 401

    return render_template("login.html")


@user_bp.route("/logout")
@login_required
def logout():
    if request.method == "GET":
        get_flashed_messages()

    logout_user()
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("landing.landing"))


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        get_flashed_messages()

    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not old_password or not new_password or not confirm:
            flash("Усі поля пароля є обов'язковими", "danger")
            return redirect(url_for("user.profile"))

        if not check_password_hash(current_user.password_hash, old_password):
            flash("Старий пароль невірний", "danger")
            return redirect(url_for("user.profile"))

        if len(new_password) < 8:
            flash("Новий пароль має містити щонайменше 8 символів", "danger")
            return redirect(url_for("user.profile"))

        if new_password != confirm:
            flash("Паролі не співпадають", "danger")
            return redirect(url_for("user.profile"))

        if check_password_hash(current_user.password_hash, new_password):
            flash("Новий пароль має відрізнятися від старого", "danger")
            return redirect(url_for("user.profile"))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Пароль успішно змінено!", "success")

        return redirect(url_for("user.profile"))

    return render_template("profile.html", user=current_user)


@user_bp.route("/settings")
def settings():
    return render_template("settings.html")
