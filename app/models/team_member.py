from . import db

class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    is_captain = db.Column(db.Boolean, default=False)

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)