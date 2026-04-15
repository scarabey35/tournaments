import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import db
from app.extension import migrate
from app.routes.landing import landing_bp
from app.routes.admin import admin
from app.routes.tournaments import tournaments_bp
from app.routes.user import user_bp
from app.routes.teams import teams_bp
from app.routes.rounds import rounds_bp

login_manager = LoginManager()
login_manager.login_view = "user.login"
login_manager.login_message = "Будь ласка, увійдіть для доступу до цієї сторінки."
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), "app", "templates"),
                static_folder=os.path.join(os.path.dirname(__file__), "app", "static"))

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'instance', 'app.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    app.register_blueprint(landing_bp)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(tournaments_bp, url_prefix="/tournaments")
    app.register_blueprint(user_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(rounds_bp)

    with app.app_context():
        db.create_all()
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
