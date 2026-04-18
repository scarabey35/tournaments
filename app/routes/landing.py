from flask import Blueprint, redirect, render_template, url_for

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
    return redirect(url_for("admin.dashboard"))


@landing_bp.route("/admin_create_tournament")
def admin_create_tournament():
    return redirect(url_for("admin.create_tournament"))
