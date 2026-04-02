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