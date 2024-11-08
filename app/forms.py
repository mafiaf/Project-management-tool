from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms_components import ColorField

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm): 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    start_time = DateTimeField('Start Time', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    end_time = DateTimeField('End Time', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    completed = BooleanField('Completed')

    priority = SelectField(
        'Priority', 
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], 
        default='Medium', 
        validators=[DataRequired()]
    )
    status = SelectField(
        'Status', 
        choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Blocked', 'Blocked'), ('Completed', 'Completed')], 
        default='Not Started', 
        validators=[DataRequired()]
    )
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    is_recurring = BooleanField('Is Recurring?')
    recurrence_frequency = SelectField(
        'Recurrence Frequency', 
        choices=[('None', 'None'),('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], 
        validators=[Optional()]
    )
    reminder_time = DateTimeField('Reminder Time', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])

    category = SelectField('Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Changes')


class ShareTaskForm(FlaskForm):
    email = StringField('Invitee Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('Viewer', 'Viewer'), ('Editor', 'Editor')], validators=[DataRequired()])
    submit = SubmitField('Share Task')
    
class CommentForm(FlaskForm):
    content = TextAreaField('Add a Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    color = ColorField('Color', default='#007bff', validators=[DataRequired()])
    priority_level = SelectField(
        'Priority Level',
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        default='Medium',
        validators=[DataRequired()]
    )
    visibility = SelectField(
        'Visibility',
        choices=[('Public', 'Public'), ('Private', 'Private')],
        default='Private',
        validators=[DataRequired()]
    )
    is_shared = BooleanField('Share this Category?')
    default_reminders = BooleanField('Default Reminders for Tasks')
    icon = StringField('Icon Path or Name', validators=[Optional()])
    archived = BooleanField('Archived')

    submit = SubmitField('Save Category')

class CancelInvitationForm(FlaskForm):
    pass

class UpdateProfileForm(FlaskForm):
    username = StringField(
        'Username', 
        validators=[
            DataRequired(), 
            Length(min=3, max=25, message="Username must be between 3 and 25 characters.")
        ]
    )
    email = StringField(
        'Email', 
        validators=[
            DataRequired(), 
            Email(message="Please enter a valid email address.")
        ]
    )
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password', 
        validators=[DataRequired(message="Please enter your current password.")]
    )
    new_password = PasswordField(
        'New Password', 
        validators=[
            DataRequired(message="Please enter a new password."),
            Length(min=8, message="Password must be at least 8 characters long."),
        ]
    )
    confirm_password = PasswordField(
        'Confirm New Password', 
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('new_password', message="Passwords must match.")
        ]
    )
    submit = SubmitField('Change Password')