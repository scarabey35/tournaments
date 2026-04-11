from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Tournament, Team, TeamMember
from app.decorators import roles_required

teams_bp=Blueprint("teams", __name__)

@teams_bp.route("/tournaments/<int:tournament_id>/register", methods=["GET", "POST"])
@login_required
@roles_required("team")
def register_team(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    now = datetime.utcnow()

    # Перевірка вікна реєстрації
    if now < tournament.registration_start:
        flash("Реєстрація ще не розпочалась.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    if now > tournament.registration_end:
        flash("Реєстрація вже закрита.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    # Якщо юзер вже в якійсь команді цього турніру
    if current_user.team_id:
        existing = Team.query.get(current_user.team_id)
        if existing and existing.tournament_id == tournament_id:
            flash("Ви вже зареєстровані в команді для цього турніру.", "warning")
            return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    # Перевірка ліміту команд
    if tournament.max_teams and len(tournament.teams) >= tournament.max_teams:
        flash("Досягнуто максимальну кількість команд.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    if request.method == "POST":
        team_name = request.form.get("team_name", "").strip()
        city = request.form.get("city", "").strip()
        organization = request.form.get("organization", "").strip()
        contact = request.form.get("contact", "").strip()

        captain_name = request.form.get("captain_name", "").strip()
        captain_email = request.form.get("captain_email", "").strip().lower()

        member_names = request.form.getlist("member_name")
        member_emails = request.form.getlist("member_email")

        # --- Валідація ---
        if not team_name:
            flash("Введіть назву команди.", "danger")
            return render_template("teams/register.html", tournament=tournament)

        if not captain_name or not captain_email:
            flash("Введіть дані капітана.", "danger")
            return render_template("teams/register.html", tournament=tournament)

        # Збираємо всіх учасників (капітан + члени)
        all_emails = [captain_email]
        members_data = []

        for i, (mname, memail) in enumerate(zip(member_names, member_emails)):
            mname = mname.strip()
            memail = memail.strip().lower()
            if mname and memail:
                members_data.append((mname, memail))
                all_emails.append(memail)

        # Мінімум 2 учасники (капітан + 1 член)
        if len(members_data) < 1:
            flash("Додайте хоча б одного учасника крім капітана.", "danger")
            return render_template("teams/register.html", tournament=tournament)

        # Унікальність email в межах команди
        if len(all_emails) != len(set(all_emails)):
            flash("Email учасників мають бути унікальними.", "danger")
            return render_template("teams/register.html", tournament=tournament)

        # Захист від дублювання: капітан вже реєстрував команду?
        existing_captain = TeamMember.query.join(Team).filter(
            Team.tournament_id == tournament_id,
            TeamMember.email == captain_email,
            TeamMember.is_captain == True,
        ).first()
        if existing_captain:
            flash("Команда з таким капітаном вже зареєстрована.", "danger")
            return render_template("teams/register.html", tournament=tournament)

        # --- Створення команди ---
        team = Team(
            name=team_name,
            city=city or None,
            organization=organization or None,
            contact=contact or None,
            tournament_id=tournament_id,
        )
        db.session.add(team)
        db.session.flush()  # отримуємо team.id до commit

        # Капітан
        captain = TeamMember(
            name=captain_name,
            email=captain_email,
            is_captain=True,
            team_id=team.id,
        )
        db.session.add(captain)

        # Величезнi члени
        for mname, memail in members_data:
            member = TeamMember(
                name=mname,
                email=memail,
                is_captain=False,
                team_id=team.id,
            )
            db.session.add(member)

        # Прив'язати юзера до команди
        current_user.team_id = team.id
        db.session.commit()

        flash(f"Команду «{team_name}» успішно зареєстровано!", "success")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    return render_template("teams/register.html", tournament=tournament)


@teams_bp.route("/teams/<int:team_id>")
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template("teams/detail.html", team=team)
