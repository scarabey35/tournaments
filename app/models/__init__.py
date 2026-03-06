from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User, UserRole

__all__ = ["db", "User", "UserRole"]