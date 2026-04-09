from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('user.login'))
            if current_user.role not in roles:
                flash("У вас немає доступу до цієї сторінки", "danger")
                return redirect(url_for('landing.landing'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
