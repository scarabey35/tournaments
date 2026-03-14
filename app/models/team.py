from app.extension import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
