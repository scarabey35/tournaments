from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required

from app.extensions import db
from app.models import User, Role

bp = Blueprint("auth", __name__)

@bp.get("/register")
def register_form():
    return render_template("register.html")

@bp.post("/register")
def register_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    role = request.form.get("role") or ""

    if role not in {r.value for r in Role}:
        abort(400, description="Invalid role")

    if not email or not password:
        abort(400, description="Email/password required")

    if User.query.filter_by(email=email).first():
        abort(409, description="User already exists")

    user = User(email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for("protected.me"))

@bp.get("/login")
def login():
    return render_template("login.html")

@bp.post("/login")
def login_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        abort(401, description="Bad credentials")

    login_user(user)
    return redirect(url_for("protected.me"))

@bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
