from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Tournament

tournaments_bp = Blueprint("tournaments", __name__)


@tournaments_bp.route("/")
def tournaments_list():
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return render_template("tournaments.html", tournaments=tournaments)


@tournaments_bp.route("/<int:tournament_id>")
def tournament_detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template("tournament_detail.html", tournament=tournament)


@tournaments_bp.route("/<int:tournament_id>/leaderboard")
def leaderboard(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template("leaderboard.html", tournament=tournament)


@tournaments_bp.route("/leaderboard")
def leaderboard_global():
    tournaments = Tournament.query.filter_by(status="finished").all()
    return render_template("leaderboard.html", tournaments=tournaments)
