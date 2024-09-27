from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .forms import RegistrationForm, LoginForm  # Import both forms
from .models import User, db
from functools import wraps

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Make sure LoginForm is imported
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(f"User found: {user}")  # Debugging line
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id  # Store the user ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            print(f"Login failed for email: {form.email.data}")  # Debugging line
    return render_template('login.html', form=form)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))
