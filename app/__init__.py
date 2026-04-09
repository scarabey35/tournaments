from flask import Flask
from flask_login import LoginManager
from .models import db
from .extension import migrate

login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    return app
