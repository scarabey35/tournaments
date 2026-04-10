from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import roles_required

admin = Blueprint("admin", __name__)


@admin.route("/")
@admin.route("/dashboard")
@login_required
@roles_required("admin")
def dashboard():
    return render_template("admin_dashboard.html")


@admin.route("/create_tournament", methods=["GET", "POST"])
@admin.route("/create-tournament", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def create_tournament():
    if request.method == "POST":
        flash("Турнір створено (заглушка)", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin_create_tournament.html")
