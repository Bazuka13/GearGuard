from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# 👇 DATABASE INSTANCE YAHIN BANEGA
db = SQLAlchemy()

# 1. DEPARTMENTS
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', backref='department', lazy=True)
    equipment = db.relationship('Equipment', backref='department', lazy=True)

# 2. TEAMS
class MaintenanceTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    technicians = db.relationship('Technician', backref='team', lazy=True)
    equipment = db.relationship('Equipment', backref='team', lazy=True)

# 3. USERS (Employees)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 4. TECHNICIANS
class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'), nullable=False)

# 5. EQUIPMENT (Machines)
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'))
    requests = db.relationship('MaintenanceRequest', backref='equipment', lazy=True)

# 6. MAINTENANCE REQUESTS
class MaintenanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='new') # new, in_progress, repaired, scrap
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration_hours = db.Column(db.Float, default=0.0)
    
    # Relationships for easy access
    technician = db.relationship('Technician', backref='requests')
    creator = db.relationship('User', backref='requests')

# 7. WORK CENTERS
class WorkCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    cost_per_hour = db.Column(db.Float, default=0.0)
    capacity_efficiency = db.Column(db.Integer, default=100)
    oee_target = db.Column(db.Integer, default=85)