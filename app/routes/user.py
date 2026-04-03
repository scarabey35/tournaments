from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

user_bp = Blueprint("user", __name__)


#REGISTER
@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if User.query.filter_by(email=email).first():
            flash("Email вже використовується", "error")
            return redirect(url_for("user.register"))

        user = User(
            name=email.split("@")[0],
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
        )

        db.session.add(user)
        db.session.commit()

        flash("Реєстрація успішна!", "success")
        return redirect(url_for("user.login"))

    return render_template("register.html")


#LOGIN
@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Невірний email або пароль", "error")
            return redirect(url_for("user.login"))

        #session
        session["user_id"] = user.id

        flash("Вхід виконано!", "success")
        return redirect(url_for("user.profile"))

    return render_template("login.html")


#LOGOUT
@user_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing.landing"))


#PROFILE
@user_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    user = User.query.get(session["user_id"])

    #password change
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not check_password_hash(user.password_hash, old_password):
            flash("Старий пароль невірний", "error")
            return redirect(url_for("user.profile"))

        if new_password != confirm_password:
            flash("Паролі не співпадають", "error")
            return redirect(url_for("user.profile"))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Пароль змінено!", "success")
        return redirect(url_for("user.profile"))

    return render_template("profile.html", user=user)

@user_bp.route("/settings")
def settings():
    return render_template("settings.html")