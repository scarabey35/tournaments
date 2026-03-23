from datetime import datetime
from . import db

class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255))
    organization = db.Column(db.String(255))

    contact = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)

    # relations
    members = db.relationship("TeamMember", backref="team", cascade="all, delete")
    submissions = db.relationship("Submission", backref="team", lazy=True)