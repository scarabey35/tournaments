from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserRole(Enum):
    ADMIN = "admin"          
    PARTICIPANT = "participant"  
    JURY = "jury"           


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.Enum(UserRole),
        nullable=False,
        default=UserRole.PARTICIPANT
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def is_participant(self) -> bool:
        return self.role == UserRole.PARTICIPANT

    def is_jury(self) -> bool:
        return self.role == UserRole.JURY

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"