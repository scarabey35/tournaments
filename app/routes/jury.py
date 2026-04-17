import random
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from app.decorators import roles_required
from app.models import db, Evaluation, Round, Submission, User

jury_bp = Blueprint("jury", __name__)


# ── ADMIN: розподіл робіт по журі ────────────────────────────────────────────

@jury_bp.route("/admin/rounds/<int:round_id>/assign", methods=["POST"])
@login_required
@roles_required("admin")
def assign_submissions(round_id):
    """
    Рандомно розподіляє сабміти між членами журі.
    Кожна робота отримує мінімум MIN_JURY_PER_SUBMISSION оцінювачів.
    Один журі не отримує одну роботу двічі.
    Можна перезапустити — видаляє старі незаповнені призначення.
    """
    MIN_JURY_PER_SUBMISSION = 2
    MAX_PER_JURY = 5

    round_ = Round.query.get_or_404(round_id)
    submissions = Submission.query.filter_by(round_id=round_id).all()
    jury_members = User.query.filter_by(role="jury").all()

    if not submissions:
        flash("Немає поданих робіт для розподілу.", "danger")
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    if not jury_members:
        flash("Немає жодного члена журі в системі.", "danger")
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    if len(jury_members) < MIN_JURY_PER_SUBMISSION:
        flash(
            f"Потрібно мінімум {MIN_JURY_PER_SUBMISSION} члени журі, "
            f"зараз є {len(jury_members)}.",
            "danger",
        )
        return redirect(url_for("rounds.round_detail", round_id=round_id))

    # Видаляємо старі незаповнені призначення (де всі оцінки None)
    old_empty = (
        Evaluation.query
        .filter(
            Evaluation.submission_id.in_([s.id for s in submissions]),
            Evaluation.backend_score.is_(None),
        )
        .all()
    )
    for ev in old_empty:
        db.session.delete(ev)
    db.session.flush()

    existing = (
        Evaluation.query
        .filter(Evaluation.submission_id.in_([s.id for s in submissions]))
        .all()
    )
    assigned: dict[int, set[int]] = {s.id: set() for s in submissions}
    for ev in existing:
        assigned[ev.submission_id].add(ev.jury_id)

    # Лічильник скільки робіт отримав кожен журі (включно з наявними)
    jury_load: dict[int, int] = {j.id: 0 for j in jury_members}
    for ev in existing:
        if ev.jury_id in jury_load:
            jury_load[ev.jury_id] += 1

    new_assignments: list[Evaluation] = []

    for sub in submissions:
        needed = max(0, MIN_JURY_PER_SUBMISSION - len(assigned[sub.id]))
        if needed == 0:
            continue

        # Кандидати: ще не призначені для цього сабміту та не перевантажені
        candidates = [
            j for j in jury_members
            if j.id not in assigned[sub.id]
            and jury_load[j.id] < MAX_PER_JURY
        ]

        if len(candidates) < needed:
            # Якщо не вистачає незавантажених — беремо будь-яких непризначених
            candidates = [
                j for j in jury_members
                if j.id not in assigned[sub.id]
            ]

        if len(candidates) < needed:
            flash(
                f"Не вдалося призначити мінімум {MIN_JURY_PER_SUBMISSION} журі "
                f"для роботи «{sub.team.name}»: замало членів журі.",
                "warning",
            )
            continue

        chosen = random.sample(candidates, needed)
        for jury in chosen:
            ev = Evaluation(submission_id=sub.id, jury_id=jury.id)
            db.session.add(ev)
            new_assignments.append(ev)
            assigned[sub.id].add(jury.id)
            jury_load[jury.id] += 1

    db.session.commit()

    flash(
        f"Розподіл завершено: {len(new_assignments)} нових призначень "
        f"для {len(submissions)} робіт і {len(jury_members)} членів журі.",
        "success",
    )
    return redirect(url_for("rounds.round_detail", round_id=round_id))


# ──список призначених робот

@jury_bp.route("/jury/assignments")
@login_required
@roles_required("jury")
def assignments():
    """Список всіх робіт призначених поточному журі."""
    evaluations = (
        Evaluation.query
        .filter_by(jury_id=current_user.id)
        .join(Submission)
        .order_by(Submission.round_id)
        .all()
    )
    return render_template("jury/assignments.html", evaluations=evaluations)


# ── форма оцiнювання

@jury_bp.route("/jury/evaluate/<int:submission_id>", methods=["GET", "POST"])
@login_required
@roles_required("jury")
def evaluate(submission_id):
    evaluation = Evaluation.query.filter_by(
        submission_id=submission_id,
        jury_id=current_user.id,
    ).first_or_404()

    submission = evaluation.submission

    # Перевірка: раунд закритий для подачі або старше
    if submission.round.status not in ("submission_closed", "evaluated"):
        flash("Оцінювання доступне лише після закриття прийому робіт.", "warning")
        return redirect(url_for("jury.assignments"))

    if request.method == "POST":
        def get_score(field: str) -> int | None:
            val = request.form.get(field, "").strip()
            if not val:
                return None
            try:
                score = int(val)
                return max(0, min(100, score))
            except ValueError:
                return None

        backend_score      = get_score("backend_score")
        database_score     = get_score("database_score")
        frontend_score     = get_score("frontend_score")
        functionality_score = get_score("functionality_score")
        usability_score    = get_score("usability_score")
        comment            = request.form.get("comment", "").strip() or None

        # Всі 5 категорій обов'язкові
        scores = [backend_score, database_score, frontend_score,
                  functionality_score, usability_score]
        if any(s is None for s in scores):
            flash("Заповніть усі 5 категорій (0–100).", "danger")
            return render_template("jury/evaluate.html",
                                   evaluation=evaluation, submission=submission)

        evaluation.backend_score       = backend_score
        evaluation.database_score      = database_score
        evaluation.frontend_score      = frontend_score
        evaluation.functionality_score = functionality_score
        evaluation.usability_score     = usability_score
        evaluation.comment             = comment

        db.session.commit()
        flash("Оцінку збережено!", "success")
        return redirect(url_for("jury.assignments"))

    return render_template("jury/evaluate.html",
                           evaluation=evaluation, submission=submission)


# перегляд усiх оцiнок

@jury_bp.route("/admin/rounds/<int:round_id>/evaluations")
@login_required
@roles_required("admin")
def round_evaluations(round_id):
    """Адмін бачить усі оцінки раунду зведено по сабмітах."""
    round_ = Round.query.get_or_404(round_id)
    submissions = Submission.query.filter_by(round_id=round_id).all()

    # Для кожного сабміту рахуємо середні та прогрес оцінювання
    summary = []
    for sub in submissions:
        filled = [e for e in sub.evaluations if e.backend_score is not None]
        total = len(sub.evaluations)

        if filled:
            avg_total = sum(
                (e.backend_score + e.database_score + e.frontend_score +
                 e.functionality_score + e.usability_score) / 5
                for e in filled
            ) / len(filled)
        else:
            avg_total = None

        summary.append({
            "submission": sub,
            "filled": len(filled),
            "total": total,
            "avg_total": round(avg_total, 1) if avg_total is not None else None,
        })

    # Сортуємо: спочатку оцінені, потім за середнім балом
    summary.sort(key=lambda x: (-(x["filled"]), -(x["avg_total"] or 0)))

    return render_template(
        "jury/round_evaluations.html",
        round=round_,
        summary=summary,
    )
