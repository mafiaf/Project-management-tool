from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from app.models import db, category_user, task_user  # Import db and other models/tables needed
from flask_wtf.csrf import validate_csrf, CSRFError

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if the user is logged in
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles, context='global', context_id=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            context_value = context_id(**kwargs) if callable(context_id) else kwargs.get(context_id, context_id)
            
            # Fetch role depending on the context (task or category)
            user_role = None
            if context == 'category' and context_value:
                user_role = db.session.query(category_user.c.role).filter_by(category_id=context_value, user_id=user_id).first()
            elif context == 'task' and context_value:
                user_role = db.session.query(task_user.c.role).filter_by(task_id=context_value, user_id=user_id).first()

            # Normalize both user role and required roles to uppercase for comparison
            user_role_upper = user_role[0].upper() if user_role else None
            roles_upper = [role.upper() for role in roles]

            # Debugging statements
            print(f"User ID: {user_id}, Context ID: {context_value}, Role Retrieved: {user_role_upper}, Required roles: {roles_upper}")

            if user_role_upper not in roles_upper:
                if request.is_json:
                    # For AJAX requests, return a JSON response
                    print("Permission denied for AJAX request.")
                    return jsonify({"success": False, "error": "You do not have permission to access this page."}), 403
                else:
                    # For standard web requests, return a flash message and redirect
                    print("Permission denied for standard web request.")
                    flash('You do not have permission to access this page.', 'danger')
                    return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


