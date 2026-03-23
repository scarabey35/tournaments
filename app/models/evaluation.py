from datetime import datetime
from . import db

class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)

    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    jury_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # scores (0–100)
    backend_score = db.Column(db.Integer)
    database_score = db.Column(db.Integer)
    frontend_score = db.Column(db.Integer)

    functionality_score = db.Column(db.Integer)
    usability_score = db.Column(db.Integer)

    comment = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("submission_id", "jury_id", name="unique_jury_submission"),
    )