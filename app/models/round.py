from datetime import datetime
from . import db

class Round(db.Model):
    __tablename__ = "rounds"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    requirements = db.Column(db.Text)
    must_have = db.Column(db.Text)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(50), default="draft")  
    # draft / active / submission_closed / evaluated

    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)

    # relations
    submissions = db.relationship("Submission", backref="round", lazy=True)