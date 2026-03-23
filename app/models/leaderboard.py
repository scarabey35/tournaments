from . import db

class Leaderboard(db.Model):
    __tablename__ = "leaderboards"

    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)

    total_score = db.Column(db.Float, nullable=False)

    rank = db.Column(db.Integer)