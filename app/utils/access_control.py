from functools import wraps
from flask import redirect, url_for, flash, session
from ..models import User  # Adjust import as per your project structure

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash("You need to log in to access this page.", "danger")
                return redirect(url_for('main.login'))

            user = User.query.get(user_id)
            if not user:
                flash("User not found. Please log in again.", "danger")
                return redirect(url_for('main.login'))

            # Automatically set the user to admin if they create a category or task
            if user.role is None:
                user.role = 'OWNER'  # Assuming 'ADMIN' is the role you want to assign

            if user.role not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('main.dashboard'))

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
