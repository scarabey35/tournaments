from datetime import datetime
from . import db

class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    github_url = db.Column(db.String(500), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)

    live_demo_url = db.Column(db.String(500))
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)

    # relations
    evaluations = db.relationship("Evaluation", backref="submission", lazy=True)