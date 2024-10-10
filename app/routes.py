from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .forms import RegistrationForm, LoginForm  # Import both forms
from .models import User, db
from .utils import login_required  # Import the login_required from utils.py
import logging

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
    tasks = user.tasks if user else []  # Get tasks associated with the user
    return render_template('dashboard.html', tasks=tasks)


@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))
