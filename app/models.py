from datetime import datetime
from .extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scan_tasks = db.relationship('ScanTask', backref='user', lazy='dynamic')

class ScanTask(db.Model):
    __tablename__ = 'scan_task'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    target_path = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')   # pending/running/completed/failed/cancelled
    cancel_requested = db.Column(db.Boolean, default=False)
    result = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)