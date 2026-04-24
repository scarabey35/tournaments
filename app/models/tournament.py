from datetime import datetime
from . import db

class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    start_date = db.Column(db.DateTime)

    registration_start = db.Column(db.DateTime, nullable=False)
    registration_end = db.Column(db.DateTime, nullable=False)

    max_teams = db.Column(db.Integer)

    status = db.Column(db.String(50), default="draft")  
    # draft / registration / running / finished

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # relations
    teams = db.relationship("Team", backref="tournament", lazy=True)
    rounds = db.relationship("Round", backref="tournament", lazy=True)
    creator = db.relationship("User", backref="tournaments", lazy=True)