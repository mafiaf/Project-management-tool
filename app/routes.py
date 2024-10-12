from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .models import User, Task, db, TaskInvitation, task_user, Category  #Model imports
from .forms import RegistrationForm, LoginForm, TaskForm, ShareTaskForm   # Import the forms
from .utils import login_required  # Import the login_required decorator
import logging  # Import logging for debugging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        existing_user_username = User.query.filter_by(username=form.username.data).first()

        if existing_user_email:
            flash('Email already exists. Please use a different email.', 'danger')
            print("Redirected to register: Email already exists.")  # Debug print
            return render_template('register.html', form=form)

        if existing_user_username:
            flash('Username already exists. Please use a different username.', 'danger')
            print("Redirected to register: Username already exists.")  # Debug print
            return render_template('register.html', form=form)

        # If no conflicts, create a new user
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        print("User registered successfully.")
        return redirect(url_for('main.login'))

    # If form is not validated on submit, just render the page again
    print("Form validation failed or GET request.")
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            logger.info(f"User {user.email} logged in successfully")
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            logger.warning(f"Failed login attempt for email: {form.email.data}")
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # Get tasks associated with the user
    tasks = user.tasks if user else []

    # Get pending invitations for the logged-in user
    invitations = TaskInvitation.query.filter_by(invitee_id=user_id, status='Pending').all()

    return render_template('dashboard.html', tasks=tasks, invitations=invitations)



@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        # Create a new task
        new_task = Task(title=form.title.data, description=form.description.data, category_id=None)
        db.session.add(new_task)
        db.session.commit()

        # Add the user as the owner of the task in the task_user table
        user_id = session.get('user_id')
        stmt = task_user.insert().values(task_id=new_task.id, user_id=user_id, role='Owner')
        db.session.execute(stmt)
        db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    # Pass different context values for adding a task
    return render_template('add_task.html', form=form, title="Add New Task", heading="Add New Task", submit_label="Add Task")



@main.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Check if user has permission to edit the task (must be the owner or an editor)
    user_id = session.get('user_id')
    task_users = [user.id for user in task.users]

    if user_id not in task_users:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    # Pass different context values for editing a task
    return render_template('add_task.html', form=form, title="Edit Task", heading="Edit Task", submit_label="Save Changes")


@main.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
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
        return redirect(url_for('main.dashboard'))

    form = ShareTaskForm()
    if form.validate_on_submit():
        # Find the user to share the task with
        invitee = User.query.filter_by(email=form.email.data).first()
        if invitee is None:
            flash('User with that email does not exist.', 'danger')
            return redirect(url_for('main.share_task', task_id=task.id))

        # Create a new task invitation
        invitation = TaskInvitation(task_id=task.id, inviter_id=user_id, invitee_id=invitee.id, role=form.role.data)
        db.session.add(invitation)
        db.session.commit()

        flash(f'Invitation sent to {invitee.email} as {form.role.data}.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('share_task.html', form=form, task=task)


@main.route('/invitations', methods=['GET'])
@login_required
def view_invitations():
    user_id = session.get('user_id')
    invitations = TaskInvitation.query.filter_by(invitee_id=user_id, status='Pending').all()

    return render_template('invitations.html', invitations=invitations)

@main.route('/invitation/<int:invitation_id>/accept', methods=['POST'])
@login_required
def accept_invitation(invitation_id):
    invitation = TaskInvitation.query.get_or_404(invitation_id)

    # Ensure the logged-in user is the invited person
    if invitation.invitee_id != session.get('user_id'):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.view_invitations'))

    # Add user to task and set status to accepted
    task = Task.query.get(invitation.task_id)
    invitee = User.query.get(invitation.invitee_id)
    task.users.append(invitee)

    # Set the role for the invited user
    stmt = task_user.update().where(
        (task_user.c.task_id == task.id) & (task_user.c.user_id == invitee.id)
    ).values(role=invitation.role)
    db.session.execute(stmt)

    # Update invitation status
    invitation.status = 'Accepted'
    db.session.commit()

    flash('Invitation accepted successfully!', 'success')
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
