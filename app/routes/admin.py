from flask import Blueprint, render_template, request, redirect
from app.extension import db

from app.models.tournament import Tournament
from app.models.team import Team
from app.models.submission import Submission

admin = Blueprint("admin", __name__)


@admin.route("/admin")
def admin_panel():

    tournaments = Tournament.query.all()
    teams = Team.query.all()
    submissions = Submission.query.all()

    return render_template(
        "admin.html",
        tournaments=tournaments,
        teams=teams,
        submissions=submissions
    )


@admin.route("/create_tournament", methods=["POST"])
def create_tournament():

    name = request.form["name"]
    deadline = request.form["deadline"]
    description = request.form["description"]

    tournament = Tournament(
        name=name,
        deadline=deadline,
        description=description
    )

    db.session.add(tournament)
    db.session.commit()

    return redirect("/admin")


@admin.route("/add_team/<int:tournament_id>", methods=["POST"])
def add_team(tournament_id):

    name = request.form["name"]

    team = Team(
        name=name,
        tournament_id=tournament_id
    )

    db.session.add(team)
    db.session.commit()

    return redirect("/admin")


@admin.route("/delete_team/<int:team_id>")
def delete_team(team_id):

    team = Team.query.get(team_id)

    db.session.delete(team)
    db.session.commit()

    return redirect("/admin")
