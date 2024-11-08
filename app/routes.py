from flask import Flask, session, Blueprint, render_template, redirect, url_for, flash, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from .models import User, Task, db, TaskInvitation, task_user, Category, ActivityLog, Comment, category_user   #Model imports
from .forms import RegistrationForm, LoginForm, TaskForm, ShareTaskForm, CommentForm, CategoryForm, CancelInvitationForm, UpdateProfileForm, ChangePasswordForm    # Import the forms
from app.utils import login_required, role_required
import logging  # Import logging for debugging
from datetime import datetime, timedelta
import calendar
import json
from flask_wtf.csrf import validate_csrf, CSRFError, validate_csrf
from app.utils.utils import login_required, role_required
from sqlalchemy import and_


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email or username already exists
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        existing_user_username = User.query.filter_by(username=form.username.data).first()

        if existing_user_email:
            return jsonify({"success": False, "message": "Email already exists. Please use a different email."}), 400
        if existing_user_username:
            return jsonify({"success": False, "message": "Username already exists. Please use a different username."}), 400

        # If no conflicts, create a new user
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        user.role = 'ADMIN'

        db.session.add(user)
        db.session.commit()

        return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 200
    else:
        # Send all validation errors back to the user
        errors = form.errors
        error_messages = []
        for field, error_list in errors.items():
            for error in error_list:
                error_messages.append(f"{field}: {error}")
        return jsonify({"success": False, "message": " ".join(error_messages)}), 400


@main.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    registration_form = RegistrationForm()

    if request.method == 'POST':
        if login_form.validate_on_submit():
            # Check if the user exists and the password is correct
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and user.check_password(login_form.password.data):
                session['user_id'] = user.id
                session['user_role'] = user.role.name  # Assuming `user.role` has a `name` attribute
                return jsonify({"success": True, "redirect_url": url_for('main.dashboard')}), 200
            else:
                # Return a JSON response indicating invalid login details
                return jsonify({"success": False, "message": "Invalid email or password."}), 400
        else:
            # Return a JSON response for form validation errors
            errors = []
            for field, field_errors in login_form.errors.items():
                for error in field_errors:
                    errors.append(f"{getattr(login_form, field).label.text}: {error}")
            return jsonify({"success": False, "message": "Form validation failed. " + " ".join(errors)}), 400

    # If a GET request, render the login template
    return render_template('login.html', login_form=login_form, registration_form=registration_form)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if 'user_id' not in session:
        flash('You need to be logged in to view your profile.', 'danger')
        return redirect(url_for('main.login'))

    # Get the current user from the session
    user = User.query.get(session['user_id'])
    if not user:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.login'))

    # Instantiate the profile update form and prefill it with user data
    form = UpdateProfileForm(obj=user)

    # Instantiate the change password form
    change_password_form = ChangePasswordForm()

    # Handle profile update
    if form.validate_on_submit() and 'update_profile' in request.form:
        # Check for email or username conflicts
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email is already in use. Please choose a different one.', 'danger')
            return render_template('profile.html', form=form, change_password_form=change_password_form, user=user)

        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username is already in use. Please choose a different one.', 'danger')
            return render_template('profile.html', form=form, change_password_form=change_password_form, user=user)

        # Update user information
        user.email = form.email.data
        user.username = form.username.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return render_template('profile.html', form=form, change_password_form=change_password_form, user=user)

@main.route('/change_password', methods=['POST'])
@login_required
def change_password():
    # Fetch current user
    user = User.query.get(session['user_id'])
    if not user:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.login'))

    change_password_form = ChangePasswordForm()

    # Profile update form (assuming it's also on the same page)
    update_profile_form = UpdateProfileForm()

    if change_password_form.validate_on_submit():
        # Verify current password matches the stored password hash
        if not user.check_password(change_password_form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        # Check if new password matches the current password
        elif user.check_password(change_password_form.new_password.data):
            flash('New password must be different from the current password.', 'danger')
        # Verify new password and confirmation match
        elif change_password_form.new_password.data != change_password_form.confirm_password.data:
            flash('New password and confirmation do not match.', 'danger')
        else:
            # Update password (hash it)
            user.set_password(change_password_form.new_password.data)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('main.profile'))

    return render_template('profile.html', form=update_profile_form, change_password_form=change_password_form, user=user)



@main.route('/my_tasks', methods=['GET'])
@login_required
def my_tasks():
    user_id = session.get('user_id')

    # Get the selected category filter from the request
    selected_category = request.args.get('category_filter', type=int)

    # Get all categories owned by the logged-in user
    categories = Category.query.filter_by(user_id=user_id).all()

    # Get all tasks owned by the user
    owned_tasks_query = Task.query.filter(Task.user_id == user_id)

    # Get tasks shared with the user (excluding owned tasks), along with the role
    shared_tasks_query = (
        db.session.query(Task, task_user.c.role)
        .join(task_user, task_user.c.task_id == Task.id)
        .filter(task_user.c.user_id == user_id, Task.user_id != user_id)
    )

    if selected_category is not None:
        owned_tasks_query = owned_tasks_query.filter_by(category_id=selected_category)
        shared_tasks_query = shared_tasks_query.filter(Task.category_id == selected_category)

    owned_tasks = owned_tasks_query.all()
    shared_tasks = shared_tasks_query.all()

    uncategorized_tasks = Task.query.filter(Task.user_id == user_id, Task.category_id == None).all()

    # Debugging
    logger.info(f"Owned tasks for user {user_id}: {[task.title for task in owned_tasks]}")
    logger.info(f"Shared tasks for user {user_id}: {[task.title for task, role in shared_tasks]}")
    logger.info(f"Uncategorized tasks for user {user_id}: {[task.title for task in uncategorized_tasks]}")

    return render_template(
        'my_tasks.html',
        categories=categories,
        owned_tasks=owned_tasks,
        shared_tasks=shared_tasks,
        uncategorized_tasks=uncategorized_tasks,
        selected_category=selected_category
    )

@main.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')

@main.route('/statistics', methods=['GET'])
@login_required
def statistics():
    return render_template('statistics.html')

@main.route('/calendar', methods=['GET'])
@login_required
def calendar():
    return render_template('calendar.html')


@main.route('/add_task', methods=['POST'])
@login_required
def add_task():
    """Route to add a new task, optionally within a specific category"""
    user_id = session.get('user_id')

    # Set up the task form and add category choices for the logged-in user
    form = TaskForm()
    categories = Category.query.filter_by(user_id=user_id).all()
    form.category.choices = [(-1, "No Category")] + [(c.id, c.name) for c in categories]

    # If category_id is provided by form submission, set it
    category_id = form.category.data

    # Set default start_time if it is not provided by the form
    if not form.start_time.data:
        form.start_time.data = datetime.now()

    if form.validate_on_submit():
        # Set category_id to None if "No Category" is selected
        if category_id == -1:
            category_id = None

        try:
            # Create a new task with the selected category and assign user_id
            new_task = Task(
                title=form.title.data,
                description=form.description.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                category_id=category_id,
                user_id=user_id,
                completed=form.completed.data,
                priority=form.priority.data,
                status=form.status.data,
                tags=form.tags.data,
                is_recurring=form.is_recurring.data,
                recurrence_frequency=form.recurrence_frequency.data,
                reminder_time=form.reminder_time.data
            )
            db.session.add(new_task)
            db.session.commit()

            # Add the user as the admin of the task in the task_user table
            stmt = task_user.insert().values(task_id=new_task.id, user_id=user_id, role='ADMIN')
            db.session.execute(stmt)
            db.session.commit()

            # Log task creation activity
            activity = ActivityLog(
                description=f"Task '{new_task.title}' created by user {user_id}",
                user_id=user_id,
                task_id=new_task.id
            )
            db.session.add(activity)
            db.session.commit()

            flash('Task added successfully!', 'success')
            return redirect(url_for('main.view_category', category_id=category_id) if category_id else url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback() 
            flash(f'An error occurred while adding the task: {str(e)}', 'danger')
            logger.error(f"Error occurred: {e}")

    if form.errors:
        logger.error(f"Form validation errors: {form.errors}")
        flash(f"Form validation errors: {form.errors}", "danger")

    return redirect(url_for('main.view_category', category_id=category_id) if category_id else url_for('main.dashboard'))



# Update Task - Drag and Drop functionality
@main.route('/update_task', methods=['POST'])
@login_required
def update_task():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON data'}), 400

        task_id = data.get('id')
        new_start_time = data.get('new_start_time')
        new_end_time = data.get('new_end_time')

        if not task_id or not new_start_time:
            return jsonify({'status': 'error', 'message': 'Missing task ID or start time'}), 400

        # Convert start and end times from ISO format to datetime objects
        task = Task.query.get(task_id)
        if task:
            task.start_time = datetime.fromisoformat(new_start_time)
            if new_end_time:
                task.end_time = datetime.fromisoformat(new_end_time)
            else:
                task.end_time = None
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Handling Recurring Tasks Logic
@main.route('/handle_recurring_tasks')
@login_required
def handle_recurring_tasks():
    tasks = Task.query.all()
    today = datetime.now().date()
    
    for task in tasks:
        if task.recurring:
            if task.recurring == 'daily':
                while task.start_time.date() < today:
                    task.start_time += timedelta(days=1)
                    task.end_time += timedelta(days=1)
            elif task.recurring == 'weekly':
                while task.start_time.date() < today:
                    task.start_time += timedelta(weeks=1)
                    task.end_time += timedelta(weeks=1)
            elif task.recurring == 'monthly':
                while task.start_time.date() < today:
                    month_days = calendar.monthrange(task.start_time.year, task.start_time.month)[1]
                    task.start_time += timedelta(days=month_days)
                    task.end_time += timedelta(days=month_days)
            db.session.commit()
    return redirect(url_for('main.dashboard'))

def get_task_changes(task, form):
    changes = []

    if task.title != form.title.data:
        changes.append(f"Title changed from '{task.title}' to '{form.title.data}'")

    if task.description != form.description.data:
        old_desc = task.description if task.description else "None"
        new_desc = form.description.data if form.description.data else "None"
        changes.append(f"Description changed from '{old_desc}' to '{new_desc}'")

    return changes

@main.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Verify Ownership
    role_query = db.session.query(task_user.c.role).filter(task_user.c.task_id == task.id, task_user.c.user_id == user_id).first()
    if user_id != task.user_id and (role_query is None or role_query[0] not in ['Editor', 'ADMIN']):
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = TaskForm(obj=task)
    
    # Populate the category field
    categories = Category.query.filter_by(user_id=user_id).all()
    form.category.choices = [(-1, "No Category")] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        changes = get_task_changes(task, form)

        task.title = form.title.data
        task.description = form.description.data
        category_id = form.category.data
        if category_id == -1:
            task.category_id = None
        else:
            task.category_id = category_id

        db.session.commit()

        for change in changes:
            activity = ActivityLog(
                description=change,
                user_id=user_id,
                task_id=task.id
            )
            db.session.add(activity)
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    form.category.data = task.category_id if task.category_id is not None else -1

    if form.errors:
        flash('There were errors in the form. Please correct them.', 'danger')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')

    return render_template('edit_task.html', form=form, task=task, title="Edit Task", heading="Edit Task", submit_label="Save Changes")



@main.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
@role_required('ADMIN', 'OWNER', context='task', context_id=lambda **kwargs: kwargs.get('task_id'))
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    user_id = session.get('user_id')

    # Verify Ownership
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()
    if not task_user_entry and task.category.user_id != user_id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    category_id = task.category_id

    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the task: {str(e)}', 'danger')

    return redirect(url_for('main.view_category', category_id=category_id) if category_id else url_for('main.dashboard'))



# Debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@main.route('/share_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def share_task(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Verify Ownership
    result = db.session.execute(
        db.select(task_user).where(
            and_(
                task_user.c.task_id == task.id,
                task_user.c.user_id == user_id,
                task_user.c.role.in_(['Owner', 'ADMIN'])
            )
        )
    ).first()

    if result is None:
        flash('Only the owner can share this task.', 'danger')
        logger.warning("User %s attempted to share task %d, but is not the owner.", user_id, task_id)
        return redirect(url_for('main.categories'))

    form = ShareTaskForm()

    if form.validate_on_submit():
        logger.info("Form validated for sharing task.")

        # Find the user to share the task with
        invitee = User.query.filter_by(email=form.email.data).first()
        if invitee is None:
            flash('User with that email does not exist.', 'danger')
            logger.warning("User with email %s does not exist.", form.email.data)
            return redirect(url_for('main.share_task', task_id=task.id))

        # Create a new task invitation
        invitation = TaskInvitation(task_id=task.id, inviter_id=user_id, invitee_id=invitee.id, role=form.role.data)
        db.session.add(invitation)
        db.session.commit()

        flash(f'Invitation sent to {invitee.email} as {form.role.data}.', 'success')
        logger.info("Invitation sent to %s for task %d with role %s.", invitee.email, task.id, form.role.data)
        return redirect(url_for('main.dashboard'))
    
    if form.errors:
        logger.warning("Form validation errors: %s", form.errors)

    logger.info("Form not submitted or not valid, displaying share task form.")

    users_assigned = (
        db.session.query(User, task_user.c.role)
        .join(task_user, task_user.c.user_id == User.id)
        .filter(task_user.c.task_id == task.id)
        .all()
    )

    users = User.query.all()

    return render_template(
        'manage_task_users.html',
        form=form,
        task=task,
        users_assigned=users_assigned,
        users=users
    )

@main.route('/manage_task_users/<int:task_id>', methods=['GET', 'POST'])
@login_required
def manage_task_users(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Verify Ownership
    role_query = db.session.query(task_user.c.role).filter(task_user.c.task_id == task.id, task_user.c.user_id == user_id).first()
    if role_query is None or role_query[0] not in ['Owner', 'ADMIN']:
        flash('You do not have permission to manage users for this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Get all users assigned to this task
    users_assigned = (
        db.session.query(User, task_user.c.role)
        .join(task_user, task_user.c.user_id == User.id)
        .filter(task_user.c.task_id == task.id)
        .all()
    )

    invitations = TaskInvitation.query.filter_by(task_id=task.id, status='Pending').all()

    form = ShareTaskForm()
    if form.validate_on_submit():
        invitee = User.query.filter_by(email=form.email.data).first()
        if invitee is None:
            flash('User with that email does not exist.', 'danger')
            return redirect(url_for('main.manage_task_users', task_id=task.id))

        invitation = TaskInvitation(task_id=task.id, inviter_id=user_id, invitee_id=invitee.id, role=form.role.data)
        db.session.add(invitation)
        db.session.commit()

        flash(f'Invitation sent to {invitee.email} as {form.role.data}.', 'success')
        return redirect(url_for('main.manage_task_users', task_id=task.id))

    return render_template(
        'manage_task_users.html',
        form=form,
        task=task,
        users_assigned=users_assigned,
        invitations=invitations
    )


@main.route('/invitations', methods=['GET'])
@login_required
def view_invitations():
    user_id = session.get('user_id')

    # Verify invitations
    invitations_received = TaskInvitation.query.filter_by(invitee_id=user_id, status='Pending').all()
    invitations_sent = TaskInvitation.query.filter_by(inviter_id=user_id, status='Pending').all()

    form = CancelInvitationForm()

    return render_template('invitations.html', invitations_received=invitations_received, invitations_sent=invitations_sent, form=form)


@main.route('/invitation/<int:invitation_id>/cancel', methods=['POST'])
@login_required
def cancel_invitation(invitation_id):
    invitation = TaskInvitation.query.get_or_404(invitation_id)
    user_id = session.get('user_id')

    # Ensure the logged-in user is the inviter
    if invitation.inviter_id != user_id:
        flash('You do not have permission to cancel this invitation.', 'danger')
        return redirect(url_for('main.view_invitations'))

    try:
        # Delete the invitation if it's pending
        db.session.delete(invitation)
        db.session.commit()
        flash('Invitation canceled successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while canceling the invitation.', 'danger')
        print(f"Error occurred while canceling invitation: {e}")

    return redirect(url_for('main.view_invitations'))

@main.route('/invitation/<int:invitation_id>/accept', methods=['POST'])
@login_required
def accept_invitation(invitation_id):
    invitation = TaskInvitation.query.get_or_404(invitation_id)

    # Verify Ownership
    user_id = session.get('user_id')
    if invitation.invitee_id != user_id:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.view_invitations'))

    try:
        stmt = task_user.insert().values(task_id=invitation.task_id, user_id=invitation.invitee_id, role=invitation.role)
        db.session.execute(stmt)

        invitation.status = 'Accepted'
        db.session.commit()

        flash('Invitation accepted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while accepting the invitation.', 'danger')
        print(f"Error occurred while accepting invitation: {e}")

    return redirect(url_for('main.dashboard'))


@main.route('/invitation/<int:invitation_id>/decline', methods=['POST'])
@login_required
def decline_invitation(invitation_id):
    invitation = TaskInvitation.query.get_or_404(invitation_id)

    # Verify Ownership 
    if invitation.invitee_id != session.get('user_id'):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.view_invitations'))

    # Update invitation status
    invitation.status = 'Declined'
    db.session.commit()

    flash('Invitation declined.', 'info')
    return redirect(url_for('main.view_invitations'))

@main.route('/task/<int:task_id>/toggle_done', methods=['POST'])
@login_required
def toggle_task_done(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Verify Ownership
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()

    # Update permission check to allow the task owner or Editor/Admin role
    if task.user_id != user_id and (not task_user_entry or task_user_entry.role not in ['EDITOR', 'ADMIN']):
        flash("You don't have permission to modify this task's completion status.", 'danger')
        return redirect(url_for('main.view_category', category_id=task.category_id))

    # Toggle the completed status
    task.completed = not task.completed
    db.session.commit()

    status = 'completed' if task.completed else 'not completed'
    flash(f'Task marked as {status}!', 'success')
    return redirect(url_for('main.view_category', category_id=task.category_id))


@main.route('/uncategorized_tasks', methods=['GET'])
@login_required
def uncategorized_tasks():
    user_id = session.get('user_id')
    
    # Fetch uncategorized tasks
    uncategorized_tasks = Task.query.filter(Task.user_id == user_id, Task.category_id == None).all()
    print(f"Uncategorized Tasks Without User Filter: {len(uncategorized_tasks)}")
    
    # Bugfix
    for task in uncategorized_tasks:
        print(f"Task ID: {task.id}, Title: {task.title}, User ID: {task.user_id}, Category ID: {task.category_id}")

    return render_template('uncategorized_tasks.html', uncategorized_tasks=uncategorized_tasks)


@main.route('/task/<int:task_id>/manage_users', methods=['GET', 'POST'])
@login_required
def manage_task_users_for_task(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Verify Ownership or Admin role
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()
    if not task_user_entry or task_user_entry.role not in ['OWNER', 'ADMIN']:
        flash("You do not have permission to manage users for this task.", 'danger')
        return render_template(
            'view_task.html',
            task=task
        )

    # Proceed to handle management actions if user has permission
    form = ShareTaskForm()

    if request.method == 'POST':
        action = request.form.get('action')
        selected_user_id = request.form.get('user_id')

        if action == 'remove':
            db.session.query(task_user).filter_by(task_id=task.id, user_id=selected_user_id).delete()
            db.session.commit()
            flash('User removed from the task successfully.', 'success')

        elif action == 'update_role':
            new_role = request.form.get('role')
            stmt = task_user.update().where(
                (task_user.c.task_id == task.id) & (task_user.c.user_id == selected_user_id)
            ).values(role=new_role)
            db.session.execute(stmt)
            db.session.commit()
            flash('User role updated successfully.', 'success')

        elif action == 'add' and form.validate_on_submit():
            new_user_id = request.form.get('user_id')
            new_role = request.form.get('role')

            existing_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=new_user_id).first()
            if existing_entry:
                flash('This user is already assigned to the task.', 'warning')
            else:
                stmt = task_user.insert().values(task_id=task.id, user_id=new_user_id, role=new_role)
                db.session.execute(stmt)
                db.session.commit()
                flash('User added to the task successfully.', 'success')

    users_assigned = (
        db.session.query(User, task_user.c.role)
        .join(task_user, task_user.c.user_id == User.id)
        .filter(task_user.c.task_id == task.id)
        .all()
    )

    users = User.query.all()

    return render_template(
        'manage_task_users.html',
        task=task,
        users_assigned=users_assigned,
        users=users,
        form=form
    )


# Conflict Detection
@main.route('/check_task_conflict', methods=['POST'])
@login_required
def check_task_conflict():
    start_time = datetime.strptime(request.form.get('start_time'), "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(request.form.get('end_time'), "%Y-%m-%d %H:%M")
    conflicting_tasks = Task.query.filter(
        (Task.start_time < end_time) & (Task.end_time > start_time)
    ).all()
    
    if conflicting_tasks:
        return jsonify({'status': 'conflict', 'message': 'Scheduling conflict detected'})
    return jsonify({'status': 'available'})

@main.route('/calendar', methods=['GET'])
@login_required
def task_calendar():
    return render_template('calendar.html')

@main.route('/task/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    # Fetch the task or return a 404 if not found
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Fetch the user's role in this task
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()

    # Check if the user has permission to view the task
    if not task_user_entry:
        flash('You do not have permission to view this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Render the view task page with the fetched task and user's role in this task
    return render_template(
        'view_task.html',
        task=task,
        task_user_entry=task_user_entry
    )


@main.route('/task/<int:task_id>/comments', methods=['GET', 'POST'])
@login_required
def task_comments(task_id):
    task = Task.query.get_or_404(task_id)
    form = CommentForm()
    user_id = session.get('user_id')

    # Count prerequisit for comments
    user_task_count = db.session.query(Task).filter_by(user_id=user_id).count()
    if user_task_count < 5:
        flash("You need to create at least 5 tasks before you can comment on tasks.", "warning")
        return redirect(url_for('main.view_task', task_id=task_id))

    if form.validate_on_submit():
        new_comment = Comment(content=form.content.data, user_id=user_id, task_id=task_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('main.task_comments', task_id=task_id))

    comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.timestamp.desc()).all()
    return render_template('task_comments.html', task=task, form=form, comments=comments)


@main.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    user_id = session.get('user_id')

    if form.validate_on_submit():
        color_value = str(form.color.data) if isinstance(form.color.data, str) else form.color.data.hex

        new_category = Category(
            name=form.name.data,
            description=form.description.data,
            color=color_value,
            user_id=user_id
        )
        db.session.add(new_category)
        db.session.commit()

        activity = ActivityLog(
            description=f"Category '{new_category.name}' created by user {user_id}",
            user_id=user_id,
            category_id=new_category.id
        )
        db.session.add(activity)
        db.session.commit()

        flash('Category created successfully!', 'success')
        return redirect(url_for('main.categories'))

    # Get all categories owned by the user
    user_categories = Category.query.filter_by(user_id=user_id).all()
    return render_template('categories.html', form=form, categories=user_categories)

@main.route('/category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def view_category(category_id):
    """Route to view the details of a specific category and its tasks"""
    user_id = session.get('user_id')
    category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()

    # Get all tasks in the selected category
    tasks = Task.query.filter_by(category_id=category_id).all()
    form = TaskForm()
    categories = Category.query.filter_by(user_id=user_id).all()
    form.category.choices = [(-1, "No Category")] + [(c.id, c.name) for c in categories]

    return render_template('view_category.html', category=category, tasks=tasks, form=form)



@main.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN', 'OWNER', context='category', context_id=lambda **kwargs: kwargs.get('category_id'))
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    user_id = session.get('user_id')

    # Verify Ownership
    user_role = db.session.query(category_user.c.role).filter_by(category_id=category_id, user_id=user_id).first()
    if not user_role or user_role[0] not in ['ADMIN', 'OWNER']:
        return jsonify({"success": False, "error": "You do not have permission to edit this category."}), 403

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        csrf_token = data.get('csrf_token')
        try:
            validate_csrf(csrf_token)
        except CSRFError:
            return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Update category fields
        category.name = data.get('categoryName', category.name)
        category.description = data.get('categoryDescription', category.description)
        category.color = data.get('categoryColor', category.color)
        category.priority_level = data.get('priorityLevel', category.priority_level)
        category.visibility = data.get('visibility', category.visibility)
        category.is_shared = data.get('isShared', category.is_shared) == 'on'
        category.icon = data.get('categoryIcon', category.icon)
        category.archived = 'archived' in data  # Checkbox data

        category.updated_at = datetime.utcnow()
        db.session.commit()

        # Log changes
        activity = ActivityLog(
            description=f"Category '{category.name}' updated by user {user_id}",
            user_id=user_id,
            category_id=category.id
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({"success": True, "message": "Category updated successfully"}), 200

    return jsonify({"success": False, "error": "Invalid request format"}), 400


@main.route('/get_category_data/<int:category_id>', methods=['GET'])
@login_required
@role_required('ADMIN', 'OWNER', context='category', context_id=lambda **kwargs: kwargs.get('category_id'))
def get_category_data(category_id):
    category = Category.query.get_or_404(category_id)
    user_id = session.get('user_id')

    # Check if the logged-in user has access rights to this category
    user_role = db.session.query(category_user.c.role).filter_by(category_id=category_id, user_id=user_id).first()
    if not user_role or user_role[0] not in ['ADMIN', 'OWNER']:
        return jsonify({"success": False, "error": "You do not have permission to view this category."}), 403

    category_data = {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'priority_level': category.priority_level,
        'visibility': category.visibility,
        'is_shared': category.is_shared,
        'icon': category.icon,
        'archived': category.archived
    }

    return jsonify({"success": True, "category": category_data}), 200


@main.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
@role_required('ADMIN', 'OWNER', context='category', context_id=lambda **kwargs: kwargs.get('category_id'))
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        user_id = session.get('user_id')

        # Permission to delete
        if category.user_id != user_id:
            flash('You do not have permission to delete this category.', 'danger')
            return redirect(url_for('main.dashboard'))

        category_name = category.name

        # Delete the category
        db.session.delete(category)
        db.session.commit()

        flash(f"Category '{category_name}' deleted successfully.", 'success')
        return redirect(url_for('main.dashboard'))

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred while deleting category: {e}")
        flash('An error occurred while deleting the category.', 'danger')
        return redirect(url_for('main.dashboard'))


@main.route('/add_category', methods=['POST'])
@login_required
def add_category():
    user_id = session.get('user_id')

    print("Received form data:", request.form)

    # Field verification
    category_name = request.form.get('name')
    category_color = request.form.get('color', '#007bff')
    category_description = request.form.get('description', '')
    priority_level = request.form.get('priority_level', 'Medium')
    visibility = request.form.get('visibility', 'Private')
    is_shared = bool(request.form.get('is_shared'))
    icon = request.form.get('icon', '')
    archived = bool(request.form.get('archived'))

    # Check if category name is present
    if category_name:
        new_category = Category(
            name=category_name,
            color=category_color,
            description=category_description,
            user_id=user_id,
            priority_level=priority_level,
            visibility=visibility,
            is_shared=is_shared,
            icon=icon,
            archived=archived
        )
        db.session.add(new_category)
        db.session.commit()

        # Assign "ADMIN" role to the user for this category
        stmt = category_user.insert().values(category_id=new_category.id, user_id=user_id, role='ADMIN')
        db.session.execute(stmt)
        db.session.commit()

        flash(f"Category '{category_name}' has been successfully created.", "success")
    else:
        flash("Category name is required.", "error")

    return redirect(url_for('main.categories'))


@main.route('/mark_all_completed/<int:category_id>', methods=['POST'])
@login_required
@role_required('ADMIN', 'OWNER', context='category', context_id=lambda **kwargs: kwargs.get('category_id'))
def mark_all_completed(category_id):
    """Route to mark all tasks in a category as completed"""
    # Retrieve the category
    category = Category.query.get_or_404(category_id)

    # Verify Ownership
    if category.user_id != session.get('user_id'):
        flash('You do not have permission to mark tasks in this category as completed.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    for task in category.tasks:
        task.completed = True
    db.session.commit()
    
    flash('All tasks marked as completed!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session.get('user_id')
    task_id = request.args.get('task_id', type=int)

    # Logging for debugging purposes
    if task_id:
        logger.info(f"Fetching specific task with ID: {task_id} for user: {user_id}")
    else:
        logger.info(f"Fetching all tasks for user: {user_id}")

    # Fetch all tasks if no specific task_id is provided
    if task_id is None:
        tasks = Task.query.filter_by(user_id=user_id).all()
    else:
        tasks = Task.query.filter_by(id=task_id, user_id=user_id).all()

    # Prepare tasks for FullCalendar
    events = []
    for task in tasks:
        logger.info(f"Task found: {task.title}, Start Time: {task.start_time}, End Time: {task.end_time}")
        events.append({
            'id': task.id,
            'title': task.title,
            'start': task.start_time.strftime('%Y-%m-%dT%H:%M:%S'),  # Assuming start_time is a datetime field
            'end': task.end_time.strftime('%Y-%m-%dT%H:%M:%S') if task.end_time else None,  # End time is optional
            'color': task.category.color if task.category else '#378006',  # Use category color or default
            'url': url_for('main.view_task', task_id=task.id)  # Link to task details if needed
        })

    # Log the events being returned
    logger.info(f"Events returned: {events}")

    return jsonify(events)

@main.route('/fetch_categories', methods=['POST'])
@login_required
def fetch_categories():
    """Fetch categories based on search and filter criteria."""
    user_id = session.get('user_id')
    data = request.get_json()

    search_query = data.get('search', '').strip().lower()
    priority = data.get('priority')
    visibility = data.get('visibility')

    query = Category.query.filter_by(user_id=user_id)

    # Filters
    if search_query:
        query = query.filter(Category.name.ilike(f"%{search_query}%"))
    if priority:
        query = query.filter_by(priority_level=priority)
    if visibility:
        query = query.filter_by(visibility=visibility)

    categories = query.all()
    categories_data = [{
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'priority_level': category.priority_level,
        'visibility': category.visibility,
    } for category in categories]

    return jsonify({'categories': categories_data})


@main.route('/toggle_category_status/<int:category_id>', methods=['POST'])
@login_required
def toggle_category_status(category_id):
    """Toggle the active status of a category."""
    user_id = session.get('user_id')
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()

    if category:
        # Toggle visibility or any other status field you want to change
        category.visibility = 'Private' if category.visibility == 'Public' else 'Public'
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 404
