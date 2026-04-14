from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.decorators import roles_required
from app.models import db, Round, Submission, Team, Tournament

rounds_bp = Blueprint("rounds", __name__)


# створення раунду(адмiн)

@rounds_bp.route("/admin/tournaments/<int:tournament_id>/rounds/create", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def create_round(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        requirements = request.form.get("requirements", "").strip()
        must_have = request.form.get("must_have", "").strip()
        start_time_raw = request.form.get("start_time", "").strip()
        end_time_raw = request.form.get("end_time", "").strip()

        if not name or not start_time_raw or not end_time_raw:
            flash("Назва та час старту/дедлайну обов'язкові.", "danger")
            return render_template("rounds/create.html", tournament=tournament)

        fmt = "%Y-%m-%dT%H:%M"
        try:
            start_time = datetime.strptime(start_time_raw, fmt)
            end_time = datetime.strptime(end_time_raw, fmt)
        except ValueError:
            flash("Невірний формат дати.", "danger")
            return render_template("rounds/create.html", tournament=tournament)

        if end_time <= start_time:
            flash("Дедлайн має бути пізніше старту.", "danger")
            return render_template("rounds/create.html", tournament=tournament)

        round_ = Round(
            name=name,
            description=description or None,
            requirements=requirements or None,
            must_have=must_have or None,
            start_time=start_time,
            end_time=end_time,
            status="draft",
            tournament_id=tournament_id,
        )
        db.session.add(round_)

        # Автоматично переводимо турнір у running якщо був draft/registration
        if tournament.status in ("draft", "registration"):
            tournament.status = "running"

        db.session.commit()
        flash(f"Раунд «{name}» створено!", "success")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    return render_template("rounds/create.html", tournament=tournament)


# змiнити статус раунду(адмiн)

@rounds_bp.route("/admin/rounds/<int:round_id>/status", methods=["POST"])
@login_required
@roles_required("admin")
def change_round_status(round_id):
    round_ = Round.query.get_or_404(round_id)
    new_status = request.form.get("status", "").strip()

    allowed = {"draft", "active", "submission_closed", "evaluated"}
    if new_status not in allowed:
        flash("Невідомий статус.", "danger")
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    round_.status = new_status
    db.session.commit()
    flash(f"Статус раунду змінено на «{new_status}».", "success")
    return redirect(url_for("rounds.round_detail", round_id=round_id))


# Перегляд раунду

@rounds_bp.route("/rounds/<int:round_id>")
def round_detail(round_id):
    round_ = Round.query.get_or_404(round_id)
    now = datetime.utcnow()

    # Поточний сабміт команди (якщо є)
    my_submission = None
    if current_user.is_authenticated and current_user.team_id:
        my_submission = Submission.query.filter_by(
            round_id=round_id,
            team_id=current_user.team_id,
        ).first()

    # Час до дедлайну
    seconds_left = max(0, int((round_.end_time - now).total_seconds()))

    return render_template(
        "rounds/detail.html",
        round=round_,
        now=now,
        my_submission=my_submission,
        seconds_left=seconds_left,
    )


# Подача

@rounds_bp.route("/rounds/<int:round_id>/submit", methods=["GET", "POST"])
@login_required
@roles_required("team")
def submit(round_id):
    round_ = Round.query.get_or_404(round_id)
    now = datetime.utcnow()

    # Блокування після дедлайну
    if now > round_.end_time or round_.status == "submission_closed":
        flash("Дедлайн минув, подача заблокована.", "danger")
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    # Команда юзера
    if not current_user.team_id:
        flash("Ви не є членом жодної команди.", "danger")
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    team = Team.query.get(current_user.team_id)
    if not team or team.tournament_id != round_.tournament_id:
        flash("Ваша команда не зареєстрована в цьому турнірі.", "danger")
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    # Існуючий сабміт (для редагування)
    existing = Submission.query.filter_by(
        round_id=round_id,
        team_id=team.id,
    ).first()

    if request.method == "POST":
        github_url = request.form.get("github_url", "").strip()
        video_url = request.form.get("video_url", "").strip()
        live_demo_url = request.form.get("live_demo_url", "").strip()
        description = request.form.get("description", "").strip()

        if not github_url or not video_url:
            flash("GitHub та відео обов'язкові.", "danger")
            return render_template("submissions/submit.html",
                                   round=round_, submission=existing, team=team)

        if existing:
            existing.github_url = github_url
            existing.video_url = video_url
            existing.live_demo_url = live_demo_url or None
            existing.description = description or None
            flash("Сабміт оновлено!", "success")
        else:
            submission = Submission(
                github_url=github_url,
                video_url=video_url,
                live_demo_url=live_demo_url or None,
                description=description or None,
                team_id=team.id,
                round_id=round_id,
            )
            db.session.add(submission)
            flash("Роботу подано!", "success")

        db.session.commit()
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    return render_template("submissions/submit.html",
                           round=round_, submission=existing, team=team)
