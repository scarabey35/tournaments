import os
from flask import Flask
from app.models import db

from app.routes.landing import landing_bp
from app.routes.admin import admin
from app.routes.tournaments import tournaments_bp
from app.routes.user import user_bp

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    template_dir = os.path.join(base_dir, "app", "templates")
    static_dir = os.path.join(base_dir, "app", "static")

    instance_path = os.path.join(base_dir, "instance")
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    db_path = os.path.join(instance_path, "app.db")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )

    app.config["SECRET_KEY"] = "super-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(landing_bp)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(tournaments_bp, url_prefix="/tournaments")
    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)