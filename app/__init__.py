from flask import Flask

from .config import Config
from .extensions import init_extensions
from .errors import register_error_handlers
from .blueprints import register_blueprints
from .cli import register_cli


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.config.from_pyfile("config.py", silent=True)

    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)

    return app
