from flask import Flask
from flask_login import LoginManager
from .models import db
from .extension import migrate
import os
from .routes.landing import landing_bp
from .routes.admin import admin
from .routes.tournaments import tournaments_bp
from .routes.user import user_bp
from .routes.teams import teams_bp
from .routes.rounds import rounds_bp
from .routes.jury import jury_bp

login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
login_manager.login_message_category = "info"

def create_app(*, register_blueprints=False, create_tables=False):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev'

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///app.db'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    if register_blueprints:
        app.register_blueprint(landing_bp)
        app.register_blueprint(admin, url_prefix="/admin")
        app.register_blueprint(tournaments_bp, url_prefix="/tournaments")
        app.register_blueprint(user_bp)
        app.register_blueprint(teams_bp)
        app.register_blueprint(rounds_bp)
        app.register_blueprint(jury_bp)

    if create_tables:
        with app.app_context():
            db.create_all()

    return app
