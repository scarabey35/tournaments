from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.decorators import roles_required
from app.models import db, Tournament

tournaments_bp = Blueprint("tournaments", __name__)


@tournaments_bp.route("/")
def tournaments_list():
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return render_template("tournaments.html", tournaments=tournaments)


@tournaments_bp.route("/<int:tournament_id>")
def tournament_detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template("tournament_detail.html", tournament=tournament)


@tournaments_bp.route("/<int:tournament_id>/status", methods=["POST"])
@login_required
@roles_required("admin")
def change_status(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    new_status = request.form.get("status", "").strip()

    allowed = {"draft", "registration", "running", "finished"}
    if new_status not in allowed:
        flash("Невідомий статус.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    tournament.status = new_status
    db.session.commit()
    flash(f"Статус турніру змінено на «{new_status}».", "success")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


@tournaments_bp.route("/<int:tournament_id>/leaderboard")
def leaderboard(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template("leaderboard.html", tournament=tournament)


@tournaments_bp.route("/leaderboard")
def leaderboard_global():
    tournaments = Tournament.query.filter_by(status="finished").all()
    return render_template("leaderboard.html", tournaments=tournaments)
