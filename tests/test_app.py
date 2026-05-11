import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace

from flask import url_for
from werkzeug.datastructures import MultiDict
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app as package_create_app
from app.config import DevConfig, ProdConfig, get_config
from app.decorators import roles_required
from app.models import Evaluation, Round, Submission, Team, TeamMember, Tournament, User, db
from app.routes.admin import admin as admin_bp
from app.routes.jury import jury_bp
from app.routes.landing import landing_bp
from app.routes.rounds import rounds_bp
from app.routes.teams import teams_bp
from app.routes.tournaments import _build_leaderboard, tournaments_bp
from app.routes.user import user_bp


@pytest.fixture()
def app(tmp_path):
    app = package_create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
    )

    for bp, kwargs in [
        (landing_bp, {}),
        (user_bp, {}),
        (admin_bp, {"url_prefix": "/admin"}),
        (tournaments_bp, {"url_prefix": "/tournaments"}),
        (teams_bp, {}),
        (rounds_bp, {}),
        (jury_bp, {}),
    ]:
        app.register_blueprint(bp, **kwargs)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def endpoint_path(app, endpoint, **values):
    with app.test_request_context():
        return url_for(endpoint, **values)


def add_user(app, *, name, email, password, role, team_id=None):
    with app.app_context():
        user = User(
            name=name,
            email=email.lower(),
            password_hash=generate_password_hash(password),
            role=role,
            team_id=team_id,
        )
        db.session.add(user)
        db.session.commit()

        return user


def login(client, app, email, password):
    response = client.post(
        endpoint_path(app, "user.login"),
        data={"email": email, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 302
    return response


def logout(client, app):
    return client.post(endpoint_path(app, "user.logout"), follow_redirects=False)


def test_get_config_switches_between_dev_and_prod(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert get_config() is DevConfig

    monkeypatch.setenv("FLASK_ENV", "production")
    assert get_config() is ProdConfig

    monkeypatch.setenv("FLASK_ENV", "prod")
    assert get_config() is ProdConfig


def test_roles_required_blocks_and_allows_access(app, monkeypatch):
    import app.decorators as decorators

    protected = roles_required("admin")(lambda: "ok")

    monkeypatch.setattr(
        decorators,
        "current_user",
        SimpleNamespace(is_authenticated=False, role=None),
    )
    with app.test_request_context("/admin-area"):
        response = protected()
    assert response.status_code == 302
    assert response.headers["Location"].endswith(endpoint_path(app, "user.login"))

    monkeypatch.setattr(
        decorators,
        "current_user",
        SimpleNamespace(is_authenticated=True, role="team"),
    )
    with app.test_request_context("/admin-area"):
        response = protected()
    assert response.status_code == 302
    assert response.headers["Location"].endswith(endpoint_path(app, "landing.landing"))

    monkeypatch.setattr(
        decorators,
        "current_user",
        SimpleNamespace(is_authenticated=True, role="admin"),
    )
    with app.test_request_context("/admin-area"):
        assert protected() == "ok"


def test_register_and_change_password_flow(client, app):
    register_response = client.post(
        endpoint_path(app, "user.register"),
        data={
            "name": "Alice Example",
            "email": "Alice@Example.com",
            "password": "strongpass123",
            "role": "team",
        },
        follow_redirects=False,
    )
    assert register_response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(email="alice@example.com").first()
        assert user is not None
        assert user.role == "team"
        assert check_password_hash(user.password_hash, "strongpass123")

    change_response = client.post(
        endpoint_path(app, "user.change_password"),
        data={
            "old_password": "strongpass123",
            "new_password": "newstrongpass456",
            "confirm_password": "newstrongpass456",
        },
        follow_redirects=False,
    )
    assert change_response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(email="alice@example.com").first()
        assert user is not None
        assert check_password_hash(user.password_hash, "newstrongpass456")


def test_admin_team_submission_jury_and_leaderboard_flow(client, app):
    from datetime import datetime, timedelta, timezone
    
    with app.app_context():
        add_user(app, name="Admin", email="admin@example.com", password="adminpass123", role="admin")
        add_user(app, name="Team User", email="team@example.com", password="teampass123", role="team")
        add_user(app, name="Jury One", email="jury1@example.com", password="jurypass123", role="jury")
        add_user(app, name="Jury Two", email="jury2@example.com", password="jurypass123", role="jury")

        admin_email = "admin@example.com"
        team_user_email = "team@example.com"
        jury1_email = "jury1@example.com"
        jury2_email = "jury2@example.com"
        
        with app.app_context():
            jury1_id = User.query.filter_by(email=jury1_email).first().id
            jury2_id = User.query.filter_by(email=jury2_email).first().id

    # 2. Логін Адміна
    login(client, app, admin_email, "adminpass123")

    # Створення турніру
    now = datetime.now(timezone.utc)
    tournament_response = client.post(
        endpoint_path(app, "admin.create_tournament"),
        data={
            "title": "Hackathon 2026",
            "description": "Main event",
            "max_teams": "8",
            "start_date": now.strftime("%Y-%m-%d"),
            "registration_start": (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "registration_end": (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "submission_deadline": (now + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M"),
            "format": "online",
        },
        follow_redirects=False,
    )
    assert tournament_response.status_code == 302

    with app.app_context():
        tournament_db = Tournament.query.filter_by(name="Hackathon 2026").first()
        assert tournament_db is not None
        assert tournament_db.status == "draft"
        tournament_id = tournament_db.id

    # Створення раунду
    round_response = client.post(
        endpoint_path(app, "rounds.create_round", tournament_id=tournament_id),
        data={
            "name": "Round 1",
            "description": "Initial round",
            "requirements": "Build something useful",
            "must_have": "README",
            "start_time": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
            "end_time": (now + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
        },
        follow_redirects=False,
    )
    assert round_response.status_code == 302

    with app.app_context():
        tournament_db = db.session.get(Tournament, tournament_id)
        round_db = Round.query.filter_by(tournament_id=tournament_id, name="Round 1").first()
        assert round_db is not None
        assert tournament_db.status == "running"
        round_id = round_db.id

    # 3. Реєстрація команди (під користувачем team)
    logout(client, app)
    login(client, app, team_user_email, "teampass123")

    register_team_response = client.post(
        endpoint_path(app, "teams.register_team", tournament_id=tournament_id),
        data=MultiDict([
            ("team_name", "Alpha"),
            ("city", "Kyiv"),
            ("organization", "University"),
            ("contact", "alpha@example.com"),
            ("captain_name", "Alice"),
            ("captain_email", "captain@example.com"),
            ("member_name", "Bob"),
            ("member_email", "bob@example.com"),
        ]),
        follow_redirects=False,
    )
    assert register_team_response.status_code == 302

    with app.app_context():
        team_db = Team.query.filter_by(name="Alpha").first()
        assert team_db is not None
        team_id = team_db.id
        
        user_check = User.query.filter_by(email=team_user_email).first()
        assert user_check.team_id == team_id

    # 4. Подача роботи (Submission)
    submit_response = client.post(
        endpoint_path(app, "rounds.submit", round_id=round_id),
        data={
            "github_url": "https://github.com/example/project",
            "video_url": "https://example.com/video",
            "live_demo_url": "https://example.com/demo",
            "description": "Submission description",
        },
        follow_redirects=False,
    )
    assert submit_response.status_code == 302

    with app.app_context():
        submission_db = Submission.query.filter_by(team_id=team_id, round_id=round_id).first()
        assert submission_db is not None
        submission_id = submission_db.id

    # 5. Призначення журі (під Адміном)
    logout(client, app)
    login(client, app, admin_email, "adminpass123")

    assign_response = client.post(
        endpoint_path(app, "jury.assign_submissions", round_id=round_id),
        follow_redirects=False,
    )
    assert assign_response.status_code == 302

    with app.app_context():
        evals = Evaluation.query.filter_by(submission_id=submission_id).all()
        assert len(evals) == 2
        assert {ev.jury_id for ev in evals} == {jury1_id, jury2_id}

        r_db = db.session.get(Round, round_id)
        r_db.status = "submission_closed"
        db.session.commit()

    # 6. Оцінювання (Jury 1)
    logout(client, app)
    login(client, app, jury1_email, "jurypass123")

    evaluate_response_1 = client.post(
        endpoint_path(app, "jury.evaluate", submission_id=submission_id),
        data={
            "backend_score": "110", # має стати 100
            "database_score": "-5", # має стати 0
            "frontend_score": "80",
            "functionality_score": "70",
            "usability_score": "95",
            "comment": "Solid work",
        },
        follow_redirects=False,
    )
    assert evaluate_response_1.status_code == 302

    # 7. Оцінювання (Jury 2)
    logout(client, app)
    login(client, app, jury2_email, "jurypass123")

    evaluate_response_2 = client.post(
        endpoint_path(app, "jury.evaluate", submission_id=submission_id),
        data={
            "backend_score": "90",
            "database_score": "90",
            "frontend_score": "90",
            "functionality_score": "90",
            "usability_score": "90",
            "comment": "Consistent",
        },
        follow_redirects=False,
    )
    assert evaluate_response_2.status_code == 302

    # 8. Перевірка лідерборду
    with app.app_context():
        leaderboard = _build_leaderboard(tournament_id)
        assert len(leaderboard) == 1
        row = leaderboard[0]
        assert row["team"].id == team_id
        assert row["rank"] == 1
        assert row["total_avg"] == 79.5


def test_build_leaderboard_handles_missing_data(app):
    with app.app_context():
        tournament = Tournament(
            name="Empty Tournament",
            registration_start=datetime.utcnow() - timedelta(days=1),
            registration_end=datetime.utcnow() + timedelta(days=1),
            submission_deadline=datetime.utcnow() + timedelta(days=2),
            format="online",
            status="finished",
        )
        db.session.add(tournament)
        db.session.commit()

        assert _build_leaderboard(tournament.id) == []
