from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.decorators import roles_required
from app.models import db, Evaluation, Round, Submission, Team, Tournament

tournaments_bp = Blueprint("tournaments", __name__)


@tournaments_bp.route("/")
def tournaments_list():
    selected_statuses = request.args.getlist("status")
    allowed_statuses = {"draft", "registration", "running", "finished"}
    selected_statuses = [s for s in selected_statuses if s in allowed_statuses]

    query = Tournament.query.order_by(Tournament.created_at.desc())
    if selected_statuses:
        query = query.filter(Tournament.status.in_(selected_statuses))
    tournaments = query.all()

    my_team = None
    my_tournament = None
    my_active_round = None
    my_submission = None

    if current_user.is_authenticated and current_user.role == "team" and current_user.team_id:
        my_team = Team.query.get(current_user.team_id)
        if my_team:
            my_tournament = Tournament.query.get(my_team.tournament_id)
            if my_tournament:
                my_active_round = (
                    Round.query
                    .filter_by(tournament_id=my_tournament.id, status="active")
                    .order_by(Round.start_time.desc())
                    .first()
                )
                if my_active_round:
                    my_submission = Submission.query.filter_by(
                        round_id=my_active_round.id,
                        team_id=my_team.id,
                    ).first()

    return render_template(
        "tournaments.html",
        tournaments=tournaments,
        selected_statuses=selected_statuses,
        my_team=my_team,
        my_tournament=my_tournament,
        my_active_round=my_active_round,
        my_submission=my_submission,
    )


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
    leaderboard_data = _build_leaderboard(tournament_id)
    return render_template(
        "leaderboard.html",
        tournament=tournament,
        leaderboard=leaderboard_data,
    )


@tournaments_bp.route("/leaderboard")
def leaderboard_global():
    tournaments = Tournament.query.filter_by(status="finished").all()
    return render_template("leaderboard.html", tournaments=tournaments, leaderboard=None)


# ── Підрахунок лідерборду ─────────────────────────────────────────────────────

def _build_leaderboard(tournament_id: int) -> list[dict]:
    """
    Повертає список команд, відсортований за середнім загальним балом.
    Кожен елемент:
      rank, team, total_avg, backend, database, frontend, functionality, usability,
      submission_count, evaluations_count
    """
    # Всі раунди турніру
    rounds = Round.query.filter_by(tournament_id=tournament_id).all()
    round_ids = [r.id for r in rounds]

    if not round_ids:
        return []

    # Всі сабміти цих раундів
    submissions = (
        Submission.query
        .filter(Submission.round_id.in_(round_ids))
        .all()
    )

    if not submissions:
        return []

    # Групуємо сабміти по командах
    team_submissions: dict[int, list[Submission]] = {}
    for sub in submissions:
        team_submissions.setdefault(sub.team_id, []).append(sub)

    rows = []
    for team_id, subs in team_submissions.items():
        team = subs[0].team

        # Збираємо всі заповнені оцінки по всіх сабмітах команди
        all_evals = []
        for sub in subs:
            filled = [e for e in sub.evaluations if e.backend_score is not None]
            all_evals.extend(filled)

        if not all_evals:
            # Команда є, але оцінок немає — показуємо з нулями
            rows.append({
                "team": team,
                "total_avg": 0.0,
                "backend": 0.0,
                "database": 0.0,
                "frontend": 0.0,
                "functionality": 0.0,
                "usability": 0.0,
                "submission_count": len(subs),
                "evaluations_count": 0,
            })
            continue

        n = len(all_evals)
        backend       = round(sum(e.backend_score       for e in all_evals) / n, 1)
        database      = round(sum(e.database_score      for e in all_evals) / n, 1)
        frontend      = round(sum(e.frontend_score      for e in all_evals) / n, 1)
        functionality = round(sum(e.functionality_score for e in all_evals) / n, 1)
        usability     = round(sum(e.usability_score     for e in all_evals) / n, 1)
        total_avg     = round((backend + database + frontend + functionality + usability) / 5, 2)

        rows.append({
            "team": team,
            "total_avg": total_avg,
            "backend": backend,
            "database": database,
            "frontend": frontend,
            "functionality": functionality,
            "usability": usability,
            "submission_count": len(subs),
            "evaluations_count": n,
        })

    # Сортуємо за загальним балом
    rows.sort(key=lambda x: -x["total_avg"])

    # Додаємо місце
    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    return rows
