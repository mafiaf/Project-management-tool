from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from enum import Enum

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER)

    # Relationship to tasks - a user can own many tasks
    tasks_owned_by_user = relationship('Task', back_populates='task_owner', lazy=True)

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

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(7), nullable=False, default="#007bff")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_logs = db.relationship('ActivityLog', back_populates='category', lazy=True)

    # Relationship to Task
    tasks = db.relationship('Task', back_populates='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)  # Add Foreign Key to Category

    # Relationship to Category
    category = relationship('Category', back_populates='tasks')

    # Relationship to User
    task_owner = relationship('User', back_populates='tasks_owned_by_user')