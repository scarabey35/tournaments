from functools import wraps
from flask import Blueprint, abort
from flask_login import login_required, current_user

from app.models import Role

bp = Blueprint("protected", __name__)

def roles_required(*roles: str):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator

@bp.get("/me")
@login_required
def me():
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}

@bp.get("/organizer")
@roles_required(Role.organizer.value)
def organizer_area():
    return "Organizer area"

@bp.get("/jury")
@roles_required(Role.jury.value)
def jury_area():
    return "Jury area"

@bp.get("/participant")
@roles_required(Role.participant.value)
def participant_area():
    return "Participant area"
