from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class Role(str, Enum):
    organizer = "organizer"
    participant = "participant"
    jury = "jury"




