from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError

from app.models import db, User, UserRole

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role_value = request.form.get("role", "participant")

        # перевірка полей вводу
        if not username or not email or not password:
            flash("Усі поля обов'язкові.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Пароль має бути мінімум 6 символів.", "danger")
            return render_template("register.html")

        # перевірка ролі
        try:
            role = UserRole(role_value)
        except ValueError:
            role = UserRole.PARTICIPANT

        # перевірка існуючих користувачей 
        if User.query.filter_by(username=username).first():
            flash("Username вже використовується.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email уже используется.", "danger")
            return render_template("register.html")

        # створювання користувача
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Помилка бази даних чорт візьми.", "danger")
            return render_template("register.html")

        flash("Реєстрація успішна!", "success")
        return redirect(url_for("auth.register"))

    return render_template("register.html")
