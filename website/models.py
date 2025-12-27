from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# =========================
# Department
# =========================
class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    employees = db.relationship('User', backref='department', lazy=True)
    equipments = db.relationship('Equipment', backref='department', lazy=True)

# =========================
# Users (Employees)
# =========================
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship('MaintenanceRequest', backref='created_by_user', lazy=True)
    
    # Helper to distinguish from Technician
    @property
    def role(self):
        return 'Employee'

# =========================
# Maintenance Teams
# =========================
class MaintenanceTeam(db.Model):
    __tablename__ = 'maintenance_team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    technicians = db.relationship('Technician', backref='team', lazy=True)
    equipments = db.relationship('Equipment', backref='team', lazy=True)

# =========================
# Technicians (Pre-registered)
# =========================
class Technician(UserMixin, db.Model):
    __tablename__ = 'technician'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'), nullable=False)
    photo_url = db.Column(db.String(255))

    requests = db.relationship('MaintenanceRequest', backref='technician', lazy=True)

    @property
    def role(self):
        return 'Technician'

# =========================
# Equipment (Predefined)
# =========================
class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(150))
    photo_url = db.Column(db.String(255))

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'), nullable=False)

    requests = db.relationship('MaintenanceRequest', backref='equipment', lazy=True)

# =========================
# Maintenance Requests
# =========================
class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_request'
    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.Text, nullable=False)
    problem_image = db.Column(db.String(255))

    status = db.Column(
        db.String(50),
        default='new'   # new -> in_progress -> repaired -> scrap
    )

    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'))

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration_hours = db.Column(db.Float, default=0.0)