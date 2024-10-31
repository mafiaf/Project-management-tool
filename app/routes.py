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
def change_password():
    # Authentication check
    if 'user_id' not in session:
        flash('You need to be logged in to change your password.', 'danger')
        return redirect(url_for('main.login'))

    # Fetch current user
    user = User.query.get(session['user_id'])
    if not user:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.login'))

    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Verify current password matches the stored password hash
        if not user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('main.profile'))

        # Verify new password and confirmation match
        if form.new_password.data != form.confirm_password.data:
            flash('New password and confirmation do not match.', 'danger')
            return redirect(url_for('main.profile'))

        # Update password (hash it)
        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password updated successfully!', 'success')

    return redirect(url_for('main.profile'))


@main.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    user_id = session.get('user_id')

    # Get the selected category filter from the request
    selected_category = request.args.get('category_filter', type=int)

    # Get all categories owned by the logged-in user
    categories = Category.query.filter_by(user_id=user_id).all()

    # Calculate task statistics for each category
    for category in categories:
        # Count the total number of tasks and completed tasks within this category
        total_tasks = Task.query.filter_by(category_id=category.id).count()
        completed_tasks = Task.query.filter_by(category_id=category.id, completed=True).count()
        
        # Assign these calculated values to the category object
        category.task_count = total_tasks
        category.completed_tasks = completed_tasks

    # Get all tasks owned by the user
    owned_tasks_query = Task.query.filter(Task.user_id == user_id)

    # Get tasks shared with the user (excluding owned tasks), along with the role
    shared_tasks_query = (
        db.session.query(Task, task_user.c.role)
        .join(task_user, task_user.c.task_id == Task.id)
        .filter(task_user.c.user_id == user_id, Task.user_id != user_id)
    )

    if selected_category is not None:
        # Filter owned and shared tasks by selected category if provided
        owned_tasks_query = owned_tasks_query.filter_by(category_id=selected_category)
        shared_tasks_query = shared_tasks_query.filter(Task.category_id == selected_category)

    # Combine owned and shared tasks
    owned_tasks = owned_tasks_query.all()
    shared_tasks = shared_tasks_query.all()

    # Get pending invitations for the logged-in user
    invitations = TaskInvitation.query.filter_by(invitee_id=user_id, status='Pending').all()

    return render_template(
        'dashboard.html',
        categories=categories,
        owned_tasks=owned_tasks,
        shared_tasks=shared_tasks,
        invitations=invitations,
        selected_category=selected_category
    )


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

@main.route('/my_tasks', methods=['GET'])
@login_required
def my_tasks():
    user_id = session.get('user_id')
    tasks = Task.query.filter_by(user_id=user_id).all()
    return render_template('my_tasks.html', tasks=tasks)


@main.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    """Route to add a new task, optionally within a specific category"""
    user_id = session.get('user_id')

    # Retrieve category_id from query parameters if available
    category_id = request.args.get('category_id', type=int)

    # Set up the task form and add category choices for the logged-in user
    form = TaskForm()
    categories = Category.query.filter_by(user_id=user_id).all()

    # Add category choices, including a "No Category" option with value -1
    form.category.choices = [(-1, "No Category")] + [(c.id, c.name) for c in categories]

    # If a category_id is provided, set the default value in the form
    if category_id is not None:
        form.category.data = category_id

    # If date is passed from FullCalendar, pre-fill the start_time
    date_str = request.args.get('date', None)
    if date_str:
        form.start_time.data = datetime.strptime(date_str, '%Y-%m-%d')

    if form.validate_on_submit():
        # Set category_id to None if "No Category" is selected
        selected_category_id = form.category.data
        if selected_category_id == -1:
            selected_category_id = None

        try:
            # Create a new task with the selected category and assign user_id
            new_task = Task(
                title=form.title.data,
                description=form.description.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                category_id=selected_category_id,
                user_id=user_id  # !!Associate task with the logged-in user
            )
            db.session.add(new_task)
            db.session.commit()

            # Add the user as the owner of the task in the task_user table
            stmt = task_user.insert().values(task_id=new_task.id, user_id=user_id, role='Owner')
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
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f'An error occurred while adding the task: {str(e)}', 'danger')
            logger.error(f"Error occurred: {e}")

    # If form is not valid, print errors for debugging
    if form.errors:
        logger.error(f"Form validation errors: {form.errors}")
        flash(f"Form validation errors: {form.errors}", "danger")

    return render_template('add_task.html', form=form, title="Add New Task", heading="Add New Task", submit_label="Add Task")

# Update Task - Drag and Drop functionality
@main.route('/update_task', methods=['POST'])
@login_required
def update_task():
    try:
        data = request.get_json()  # Parse incoming JSON data
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

@main.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Ensure user has permission to edit
    role_query = db.session.query(task_user.c.role).filter(task_user.c.task_id == task.id, task_user.c.user_id == user_id).first()
    if user_id != task.user_id and (role_query is None or role_query[0] not in ['EDITOR', 'ADMIN']):
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = TaskForm(obj=task)
    
    # Populate the category field choices
    categories = Category.query.filter_by(user_id=user_id).all()
    form.category.choices = [(-1, "No Category")] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        # Track changes made to the task
        changes = get_task_changes(task, form)

        # Update the task with new data
        task.title = form.title.data
        task.description = form.description.data
        category_id = form.category.data
        if category_id == -1:
            task.category_id = None
        else:
            task.category_id = category_id

        db.session.commit()

        # Log each change
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

    # If the form is not valid, add a flash message with form errors
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
    # Check if the user has access rights to delete
    if not any(user.id == user_id for user in task.users) and task.category.user_id != user_id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

from sqlalchemy import and_

import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@main.route('/share_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def share_task(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Check if the logged-in user is the owner of the task
    result = db.session.execute(
        db.select(task_user).where(
            and_(
                task_user.c.task_id == task.id,
                task_user.c.user_id == user_id,
                task_user.c.role == 'Owner'
            )
        )
    ).first()

    if result is None:
        flash('Only the owner can share this task.', 'danger')
        logger.warning("User %s attempted to share task %d, but is not the owner.", user_id, task_id)
        return redirect(url_for('main.dashboard'))

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

    # Log if form is not validated or if it's a GET request
    logger.info("Form not submitted or not valid, displaying share task form.")

    # Get all users assigned to this task
    users_assigned = (
        db.session.query(User, task_user.c.role)
        .join(task_user, task_user.c.user_id == User.id)
        .filter(task_user.c.task_id == task.id)
        .all()
    )

    # Get all users (to potentially add to the task)
    users = User.query.all()

    return render_template(
        'manage_task_users.html',
        form=form,
        task=task,
        users_assigned=users_assigned,
        users=users
    )

@main.route('/invitations', methods=['GET'])
@login_required
def view_invitations():
    user_id = session.get('user_id')

    # Invitations received by the logged-in user
    invitations_received = TaskInvitation.query.filter_by(invitee_id=user_id, status='Pending').all()

    # Invitations sent by the logged-in user
    invitations_sent = TaskInvitation.query.filter_by(inviter_id=user_id, status='Pending').all()

    # Create an instance of the form
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

    # Ensure the logged-in user is the invited person
    user_id = session.get('user_id')
    if invitation.invitee_id != user_id:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.view_invitations'))

    try:
        # Insert the user-task association into the task_user table
        stmt = task_user.insert().values(task_id=invitation.task_id, user_id=invitation.invitee_id, role=invitation.role)
        db.session.execute(stmt)

        # Update invitation status to 'Accepted'
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

    # Ensure the logged-in user is the invited
    if invitation.invitee_id != session.get('user_id'):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.view_invitations'))

    # Update invitation status
    invitation.status = 'Declined'
    db.session.commit()

    flash('Invitation declined.', 'info')
    return redirect(url_for('main.view_invitations'))

@main.route('/task/<int:task_id>/mark_done', methods=['POST'])
@login_required
def mark_task_done(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Check if the user is either the owner or has edit rights to mark the task as done
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()

    # Update permission check to allow the task owner or Editor/Admin role
    if task.user_id != user_id and (not task_user_entry or task_user_entry.role not in ['EDITOR', 'ADMIN']):
        flash("You don't have permission to mark this task as done.", 'danger')
        return redirect(url_for('main.view_task', task_id=task_id))

    # Mark the task as completed
    task.completed = True
    db.session.commit()

    flash('Task marked as completed!', 'success')
    return redirect(url_for('main.view_task', task_id=task_id))

@main.route('/task/<int:task_id>/manage_users', methods=['GET', 'POST'])
@login_required
def manage_task_users(task_id):
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Ensure that the user has permission to manage the task
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()
    if not task_user_entry or task_user_entry.role not in ['OWNER', 'ADMIN']:
        flash("You do not have permission to manage users for this task.", 'danger')
        return redirect(url_for('main.dashboard'))

    form = ShareTaskForm()

    if request.method == 'POST':
        action = request.form.get('action')
        selected_user_id = request.form.get('user_id')

        if action == 'remove':
            # Remove user from task
            db.session.query(task_user).filter_by(task_id=task.id, user_id=selected_user_id).delete()
            db.session.commit()
            flash('User removed from the task successfully.', 'success')

        elif action == 'update_role':
            # Update user's role in the task
            new_role = request.form.get('role')
            stmt = task_user.update().where(
                (task_user.c.task_id == task.id) & (task_user.c.user_id == selected_user_id)
            ).values(role=new_role)
            db.session.execute(stmt)
            db.session.commit()
            flash('User role updated successfully.', 'success')

        elif action == 'add' and form.validate_on_submit():
            # Add new user to the task
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

    # Get all users assigned to this task
    users_assigned = (
        db.session.query(User, task_user.c.role)
        .join(task_user, task_user.c.user_id == User.id)
        .filter(task_user.c.task_id == task.id)
        .all()
    )

    # Get all users (to potentially add to the task)
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
    task = Task.query.get_or_404(task_id)
    user_id = session.get('user_id')

    # Check if the user has permission to view the task
    task_user_entry = db.session.query(task_user).filter_by(task_id=task.id, user_id=user_id).first()
    if not task_user_entry:
        flash('You do not have permission to view this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    return render_template('view_task.html', task=task)

@main.route('/task/<int:task_id>/comments', methods=['GET', 'POST'])
@login_required
def task_comments(task_id):
    task = Task.query.get_or_404(task_id)
    form = CommentForm()
    user_id = session.get('user_id')

    if form.validate_on_submit():
        new_comment = Comment(content=form.content.data, user_id=user_id, task_id=task_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('main.task_comments', task_id=task_id))

    comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.timestamp.desc()).all()
    return render_template('task_comments.html', task=task, form=form, comments=comments)


def get_task_changes(task, form):
    changes = []

    if task.title != form.title.data:
        changes.append(f"Title changed from '{task.title}' to '{form.title.data}'")

    if task.description != form.description.data:
        old_desc = task.description if task.description else "None"
        new_desc = form.description.data if form.description.data else "None"
        changes.append(f"Description changed from '{old_desc}' to '{new_desc}'")

    return changes

@main.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    user_id = session.get('user_id')

    if form.validate_on_submit():
        # Convert color to a string representation
        color_value = str(form.color.data) if isinstance(form.color.data, str) else form.color.data.hex

        # Create a new category with color
        new_category = Category(
            name=form.name.data,
            description=form.description.data,
            color=color_value,  # Save color as a hex value string
            user_id=user_id
        )
        db.session.add(new_category)
        db.session.commit()

        # Log activity for creating a category
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

@main.route('/category/<int:category_id>', methods=['GET'])
@login_required
def view_category(category_id):
    """Route to view the details of a specific category and its tasks"""
    user_id = session.get('user_id')
    category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()

    # Get all tasks in the selected category
    tasks = Task.query.filter_by(category_id=category_id).all()

    return render_template('view_category.html', category=category, tasks=tasks)


@main.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN', 'OWNER', context='category', context_id=lambda **kwargs: kwargs.get('category_id'))
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    user_id = session.get('user_id')

    # Check if the logged-in user has access rights to this category
    user_role = db.session.query(category_user.c.role).filter_by(category_id=category_id, user_id=user_id).first()
    if not user_role or user_role[0] not in ['ADMIN', 'OWNER']:
        return jsonify({"success": False, "error": "You do not have permission to edit this category."}), 403

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            # Handle form data submission if not sent as JSON
            data = request.form

        # CSRF Token Validation
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
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        user_id = session.get('user_id')

        # Ensure the user has permission to delete the category
        if category.user_id != user_id:
            flash('You do not have permission to delete this category.', 'danger')
            return redirect(url_for('main.dashboard'))

        category_name = category.name

        # Delete the category
        db.session.delete(category)
        db.session.commit()

        # Flash a success message
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

    # Log the entire request.form to see what data is being received
    print("Received form data:", request.form)

    # Use the correct field names matching the submitted data
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
        # Create the new category
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

        # Assign "Admin" role to the user for this category
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

    # Ensure the logged-in user owns the category
    if category.user_id != session.get('user_id'):
        flash('You do not have permission to mark tasks in this category as completed.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Logic to mark all tasks as completed
    for task in category.tasks:
        task.completed = True
    db.session.commit()
    
    flash('All tasks marked as completed!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session.get('user_id')
    task_id = request.args.get('task_id', type=int)  # Get task_id from query parameter if available

    # Logging for debugging purposes
    if task_id:
        logger.info(f"Fetching specific task with ID: {task_id} for user: {user_id}")
    else:
        logger.info(f"Fetching all tasks for user: {user_id}")

    # Fetch all tasks if no specific task_id is provided
    if task_id is None:
        # Get all tasks owned or shared with the user
        tasks = Task.query.filter_by(user_id=user_id).all()
    else:
        # Get the specific task
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

    # Base query
    query = Category.query.filter_by(user_id=user_id)

    # Apply search filter
    if search_query:
        query = query.filter(Category.name.ilike(f"%{search_query}%"))

    # Apply priority filter
    if priority:
        query = query.filter_by(priority_level=priority)

    # Apply visibility filter
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
