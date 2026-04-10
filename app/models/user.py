from datetime import datetime
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), nullable=False)  
    # admin / team / jury 

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relations
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True)

    evaluations = db.relationship("Evaluation", backref="jury", lazy=True)
