from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table, Column, Integer, ForeignKey, Enum, String
from enum import Enum
from flask_wtf import FlaskForm 
from wtforms import StringField, TextAreaField, DateTimeField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional 


class UserRole(Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"

# Association table for many-to-many relationship between Task and User
task_user = db.Table('task_user',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role', db.String(50))  # Role can be "Admin", "Editor", "Viewer"
)

category_user = Table(
    'category_user',
    db.Model.metadata,
    Column('category_id', Integer, ForeignKey('category.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('role', String, nullable=False)
)

# Association table for the many-to-many relationship between Task and User
task_assignees = Table(
    'task_assignees', db.Model.metadata,
    Column('task_id', Integer, ForeignKey('task.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(7), nullable=False, default="#007bff")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    priority_level = db.Column(db.Enum('Low', 'Medium', 'High', name='priority_levels'), default='Medium')
    visibility = db.Column(db.Enum('Public', 'Private', name='visibility_levels'), default='Private')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(100), nullable=True)
    default_reminders = db.Column(db.Boolean, default=False)
    archived = db.Column(db.Boolean, default=False)

    shared_with = db.relationship('User', secondary='category_user', backref='shared_categories')
    activity_logs = db.relationship('ActivityLog', back_populates='category', lazy=True)
    tasks = db.relationship('Task', back_populates='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    priority = db.Column(db.String(20), nullable=False, default='Medium')  
    status = db.Column(db.String(20), nullable=False, default='Not Started')  
    tags = db.Column(db.String(255), nullable=True)  
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_frequency = db.Column(db.String(20), nullable=True) 
    reminder_time = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category = db.relationship('Category', back_populates='tasks')
    task_owner = db.relationship('User', back_populates='tasks_owned_by_user')
    assigned_users = db.relationship('User', secondary='task_assignees', back_populates='assigned_tasks')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER)

    tasks_owned_by_user = relationship('Task', back_populates='task_owner', lazy=True)
    assigned_tasks = relationship('Task', secondary=task_assignees, back_populates='assigned_users')  # Added this line

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TaskInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # "Pending", "Accepted", "Declined"
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    task = db.relationship('Task', backref='invitations')
    inviter = db.relationship('User', foreign_keys=[inviter_id])
    invitee = db.relationship('User', foreign_keys=[invitee_id])
    
class Comment(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    task = db.relationship('Task', backref=db.backref('comments', lazy=True))


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('activity_logs', lazy=True))
    task = db.relationship('Task', backref=db.backref('activity_logs', lazy=True))
    category = db.relationship('Category', back_populates='activity_logs')
