from app.extension import db

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    project_link = db.Column(db.String(200))

    tournament_id = db.Column(
        db.Integer,
        db.ForeignKey("tournament.id")
    )
