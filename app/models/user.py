import bcrypt
from enum import Enum
from flask_login import UserMixin
from app.extensions import db


class Role(str, Enum):
    organizer = "organizer"
    participant = "participant"
    jury = "jury"


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # bcrypt-хэш — это текст вида "$2b$12$....", обычно 60 символов
    password_hash = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(32), nullable=False, index=True)

    def set_password(self, password: str) -> None:
        if not password:
            raise ValueError("Password required")

        pw_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)  # 12 — нормальный баланс; можно 10-14
        hashed = bcrypt.hashpw(pw_bytes, salt)

        # хранить удобнее строкой
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        pw_bytes = password.encode("utf-8")
        hash_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)

    def has_role(self, *roles: str) -> bool:
        return self.role in roles


