from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Tournament

admin = Blueprint("admin", __name__)


@admin.route("/")
def dashboard():
    tournaments = Tournament.query.all()
    return render_template("admin/dashboard.html", tournaments=tournaments)


@admin.route("/create_tournament", methods=["GET", "POST"])
def create_tournament():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        tournament = Tournament(
            name=name,
            description=description,
            status="draft"
        )

        db.session.add(tournament)
        db.session.commit()

        flash("Турнір створено!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/create_tournament.html")