from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.models import db, User

user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if not email or not password or not role:
            flash("Заповніть всі поля", "error")
            return redirect(url_for("user.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Користувач з таким email вже існує", "error")
            return redirect(url_for("user.register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=email.split("@")[0],
            email=email,
            password_hash=hashed_password,
            role=role,
        )

        db.session.add(user)
        db.session.commit()

        flash("Реєстрація успішна!", "success")
        return redirect(url_for("landing.home"))

    return render_template("register.html")