from flask import Blueprint, render_template

landing_bp = Blueprint("landing", __name__)

@landing_bp.route("/")
def landing():
    return render_template("landing.html")


@landing_bp.route("/home")
def home():
    return render_template("home.html")


@landing_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@landing_bp.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


@landing_bp.route("/admin_create_tournament")
def admin_create_tournament():
    return render_template("admin_create_tournament.html")
