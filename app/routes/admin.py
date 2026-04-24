from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Tournament
from app.decorators import roles_required

admin = Blueprint("admin", __name__)


@admin.route("/dashboard")
@login_required
@roles_required("admin")
def dashboard():
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return render_template("admin_dashboard.html", tournaments=tournaments)


@admin.route("/create_tournament", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def create_tournament():
    if request.method == "POST":
        name = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        max_teams_raw = request.form.get("max_teams", "").strip()
        start_date_raw = request.form.get("start_date", "").strip()
        registration_end_raw = request.form.get("registration_deadline", "").strip()
        submission_deadline_raw = request.form.get("submission_deadline", "").strip()  # FIX: було відсутнє
        format_ = request.form.get("format", "").strip()  # FIX: було відсутнє

        # --- Валідація обов'язкових полів ---
        if not name:
            flash("Назва турніру обов'язкова", "danger")
            return render_template("admin/create_tournament.html")

        if not registration_end_raw:
            flash("Вкажіть дату завершення реєстрації", "danger")
            return render_template("admin/create_tournament.html")

        if not submission_deadline_raw:
            flash("Вкажіть дедлайн здачі робіт", "danger")
            return render_template("admin/create_tournament.html")

        if not format_:
            flash("Оберіть формат турніру", "danger")
            return render_template("admin/create_tournament.html")

        # --- Парсинг дат ---
        fmt_date = "%Y-%m-%d"
        fmt_datetime = "%Y-%m-%dT%H:%M"

        try:
            registration_end = datetime.strptime(registration_end_raw, fmt_date)
            registration_start = datetime.utcnow()
        except ValueError:
            flash("Невірний формат дати реєстрації", "danger")
            return render_template("admin/create_tournament.html")

        start_date = None
        if start_date_raw:
            try:
                start_date = datetime.strptime(start_date_raw, fmt_date)
            except ValueError:
                flash("Невірний формат дати старту", "danger")
                return render_template("admin/create_tournament.html")

        try:
            submission_deadline = datetime.strptime(submission_deadline_raw, fmt_datetime)
        except ValueError:
            flash("Невірний формат дедлайну здачі робіт", "danger")
            return render_template("admin/create_tournament.html")

        max_teams = None
        if max_teams_raw:
            try:
                max_teams = int(max_teams_raw)
                if max_teams < 1:
                    raise ValueError
            except ValueError:
                flash("Максимальна кількість команд має бути > 0", "danger")
                return render_template("admin/create_tournament.html")

        # --- Створення турніру ---
        tournament = Tournament(
            name=name,
            description=description or None,
            start_date=start_date,
            registration_start=registration_start,
            registration_end=registration_end,
            submission_deadline=submission_deadline,   # FIX: додано
            format=format_,                            # FIX: додано
            max_teams=max_teams,
            status="draft",
            created_by=current_user.id,               # FIX: додано
        )
        db.session.add(tournament)
        db.session.commit()

        flash(f"Турнір «{name}» створено!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/create_tournament.html")