from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Tournament
from app.decorators import roles_required

admin = Blueprint("admin", __name__)


@admin.route("/")
@login_required
@roles_required("admin")
def dashboard():
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return render_template("admin/dashboard.html", tournaments=tournaments)


@admin.route("/create_tournament", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def create_tournament():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        max_teams_raw = request.form.get("max_teams", "").strip()
        start_date_raw = request.form.get("start_date", "").strip()
        registration_start_raw = request.form.get("registration_start", "").strip()
        registration_end_raw = request.form.get("registration_end", "").strip()

        if not name:
            flash("Назва турніру обов'язкова", "danger")
            return redirect(url_for("admin.create_tournament"))

        if not registration_start_raw or not registration_end_raw:
            flash("Вкажіть дати реєстрації", "danger")
            return redirect(url_for("admin.create_tournament"))

        fmt = "%Y-%m-%dT%H:%M"
        try:
            registration_start = datetime.strptime(registration_start_raw, fmt)
            registration_end = datetime.strptime(registration_end_raw, fmt)
        except ValueError:
            flash("Невірний формат дати", "danger")
            return redirect(url_for("admin.create_tournament"))

        if registration_end <= registration_start:
            flash("Дата закінчення реєстрації має бути пізніше початку", "danger")
            return redirect(url_for("admin.create_tournament"))

        start_date = None
        if start_date_raw:
            try:
                start_date = datetime.strptime(start_date_raw, fmt)
            except ValueError:
                flash("Невірний формат дати старту", "danger")
                return redirect(url_for("admin.create_tournament"))

        max_teams = None
        if max_teams_raw:
            try:
                max_teams = int(max_teams_raw)
                if max_teams < 1:
                    raise ValueError
            except ValueError:
                flash("Максимальна кількість команд має бути цілим числом > 0", "danger")
                return redirect(url_for("admin.create_tournament"))

        tournament = Tournament(
            name=name,
            description=description or None,
            start_date=start_date,
            registration_start=registration_start,
            registration_end=registration_end,
            max_teams=max_teams,
            status="draft",
        )

        db.session.add(tournament)
        db.session.commit()

        flash(f"Турнір «{name}» створено!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/create_tournament.html")
