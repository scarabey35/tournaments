from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user
from app.models import Tournament

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def landing():
    return render_template("landing.html")


@landing_bp.route("/home")
def home():
    admin_tournaments = []
    if current_user.is_authenticated and current_user.role == "admin":
        admin_tournaments = (
            Tournament.query.order_by(Tournament.created_at.desc()).limit(5).all()
        )
    return render_template("home.html", admin_tournaments=admin_tournaments)


@landing_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@landing_bp.route("/admin_dashboard")
def admin_dashboard():
    return redirect(url_for("admin.dashboard"))


@landing_bp.route("/admin_create_tournament")
def admin_create_tournament():
    return redirect(url_for("admin.create_tournament"))
