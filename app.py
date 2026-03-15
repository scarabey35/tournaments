from flask import Flask
import os
from app.routes.landing import landing_bp
from app.routes.admin import admin
from app.routes.tournaments import tournaments_bp




base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "app", "templates")
static_dir = os.path.join(base_dir, "app", "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.register_blueprint(admin)
app.register_blueprint(landing_bp)
app.register_blueprint(tournaments_bp)

if __name__ == "__main__":
    app.run(debug=True)
