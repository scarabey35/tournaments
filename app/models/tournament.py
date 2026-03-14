from app.extension import db

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    deadline = db.Column(db.String(100))
    description = db.Column(db.Text)

    teams = db.relationship('Team', backref='tournament', lazy=True)
