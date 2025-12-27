from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # Needed for login
from datetime import datetime

# 1. Initialize SQLAlchemy detached from the app
db = SQLAlchemy()

# ---------------------------------------------------------
# 2. DEFINE MODELS
# ---------------------------------------------------------

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    
    # Relationships
    members = db.relationship('User', backref='team', lazy=True)
    assigned_equipment = db.relationship('Equipment', backref='assigned_team', lazy=True)
    requests = db.relationship('MaintenanceRequest', backref='team', lazy=True)

class User(UserMixin, db.Model): # Note: UserMixin is required for Flask-Login
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='Technician')
    
    # Foreign Keys
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    # Relationships
    tickets_working_on = db.relationship('MaintenanceRequest', backref='technician', lazy=True)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    serial_number = db.Column(db.String(100), unique=True)
    company = db.Column(db.String(100), default='My Company (San Francisco)')
    used_by_employee = db.Column(db.String(100))
    location = db.Column(db.String(100))
    
    maintenance_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    work_center_id = db.Column(db.Integer, nullable=True) # Simplified for now
    
    health_score = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    scrap_date = db.Column(db.Date, nullable=True)
    
    maintenance_requests = db.relationship('MaintenanceRequest', backref='equipment', lazy=True)

class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    request_type = db.Column(db.String(20))
    priority = db.Column(db.Integer, default=1)
    stage = db.Column(db.String(20), default='New Request') 
    request_date = db.Column(db.Date, default=datetime.utcnow)
    scheduled_date = db.Column(db.DateTime, nullable=True)
    duration_hours = db.Column(db.Float, default=0.0)
    
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)