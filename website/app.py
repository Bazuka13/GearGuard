"""
GearGuard Flask application entrypoint.

This module:
- Configures Flask and initializes extensions (SQLAlchemy, Flask-Login).
- Registers the authentication blueprint.
- Defines protected routes for dashboard, equipment, teams, reporting, schedule,
  and maintenance requests.
Notes:
- Routes use Flask-Login decorators to require authentication.
- Keep business logic in models/services; routes should handle request/response.
"""

# ------------------------
# Imports
# ------------------------
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from os import path
from sqlalchemy import func

# Import ORM models and db object (db is a SQLAlchemy instance defined in models)
from models import db, User, Department, MaintenanceTeam, Technician, Equipment, MaintenanceRequest, WorkCenter

# ------------------------
# Application configuration
# ------------------------
app = Flask(__name__)
# Secret key used for session signing; change to secure value in production
app.config['SECRET_KEY'] = 'gearguard_secret_key_123'
# SQLAlchemy connection string — update credentials/database for your environment
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/Gearguard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ------------------------
# Initialize extensions
# ------------------------
# Bind the SQLAlchemy instance to the Flask app
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Blueprint route for login
login_manager.init_app(app)

# User loader callback required by Flask-Login
@login_manager.user_loader
def load_user(id):
    """Return a User instance for a given user id (used by Flask-Login)."""
    return User.query.get(int(id))

# Register authentication blueprint (handles login/signup/logout)
from auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/')

# ================= ROUTES =================

@app.route('/')
@login_required
def home():
    """Redirect authenticated users to the dashboard."""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard view.
    Gathers grouped maintenance requests to show on the UI (e.g. Kanban or KPI cards).
    """
    new_reqs = MaintenanceRequest.query.filter_by(status='new').all()
    progress_reqs = MaintenanceRequest.query.filter_by(status='in_progress').all()
    repaired_reqs = MaintenanceRequest.query.filter_by(status='repaired').all()
    scrap_reqs = MaintenanceRequest.query.filter_by(status='scrap').all()

    return render_template("index.html", 
                           user=current_user,
                           new_reqs=new_reqs,
                           progress_reqs=progress_reqs,
                           repaired_reqs=repaired_reqs,
                           scrap_reqs=scrap_reqs,
                           page='dashboard')

@app.route('/api/update_stage', methods=['POST'])
@login_required
def update_stage():
    """
    API endpoint to update the status/stage of a maintenance request.
    Expects JSON payload: { "task_id": <id>, "new_stage": "<label>" }.
    Maps UI labels to DB status values and commits the change.
    """
    data = request.json
    task_id = data.get('task_id')
    new_stage = data.get('new_stage')
    status_map = {'New Request': 'new', 'In Progress': 'in_progress', 'Repaired': 'repaired', 'Scrap': 'scrap'}
    db_status = status_map.get(new_stage)
    if task_id and db_status:
        req = MaintenanceRequest.query.get(task_id)
        if req:
            req.status = db_status
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/work_centers')
@login_required
def work_centers():
    """List work centers used for scheduling, costing and capacity planning."""
    centers = WorkCenter.query.all()
    return render_template("work_centers.html", centers=centers, page='work_centers')

@app.route('/equipment')
@login_required
def equipment():
    """List all equipment assets."""
    all_equipment = Equipment.query.all()
    return render_template("equipment.html", equipment=all_equipment, page='equipment')

@app.route('/equipment/<int:id>', methods=['GET', 'POST'])
@login_required
def equipment_detail(id):
    """
    View and update a single equipment record.
    - GET: render form populated with equipment and supporting lists.
    - POST: persist edited fields and redirect back to equipment list.
    """
    equipment = Equipment.query.get_or_404(id)

    if request.method == 'POST':
        # Update allowed equipment fields from the submitted form
        equipment.name = request.form.get('name')
        equipment.serial_number = request.form.get('serial_number')
        equipment.location = request.form.get('location')
        equipment.department_id = request.form.get('department')
        equipment.team_id = request.form.get('team')
        
        db.session.commit()
        flash('Equipment details updated successfully!', 'success')
        return redirect(url_for('equipment'))

    # Supporting data for form select controls
    departments = Department.query.all()
    teams = MaintenanceTeam.query.all()
    work_centers = WorkCenter.query.all()
    # Count active 'in_progress' maintenance requests for the equipment
    active_maint = MaintenanceRequest.query.filter_by(equipment_id=id, status='in_progress').count()

    return render_template('equipment_detail.html', 
                           equipment=equipment,
                           departments=departments,
                           teams=teams,
                           work_centers=work_centers,
                           active_maint=active_maint)

@app.route('/teams')
@login_required
def teams():
    """List maintenance teams and brief metadata for team management pages."""
    all_teams = MaintenanceTeam.query.all()
    return render_template("teams.html", teams=all_teams, page='teams')

@app.route('/reporting')
@login_required
def reporting():
    """
    Reporting view:
    - KPI totals
    - Average repair duration for completed tasks
    - Top equipment by request count
    - Provide placeholder chart data for the UI
    """
    total = MaintenanceRequest.query.count()
    completed = MaintenanceRequest.query.filter_by(status='repaired').count()
    
    avg_time_val = db.session.query(func.avg(MaintenanceRequest.duration_hours))\
                             .filter(MaintenanceRequest.status == 'repaired').scalar()
    avg_time = round(avg_time_val, 1) if avg_time_val else 0

    critical = MaintenanceRequest.query.filter(
        MaintenanceRequest.status.in_(['new', 'in_progress'])
    ).count()

    top_eq = db.session.query(Equipment.name, func.count(MaintenanceRequest.id))\
                       .join(MaintenanceRequest)\
                       .group_by(Equipment.name)\
                       .order_by(func.count(MaintenanceRequest.id).desc())\
                       .limit(3)\
                       .all()

    # Example/placeholder labels and values for charts; replace with real time-series data later
    chart_labels = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    chart_reqs = [total - 15, total - 10, total - 5, total + 2, total + 5, total]
    chart_comps = [completed - 12, completed - 8, completed - 4, completed, completed + 2, completed]

    return render_template("reporting.html", 
                           page='reporting',
                           total=total,
                           completed=completed,
                           avg_time=avg_time,
                           critical=critical,
                           top_eq=top_eq,
                           chart_labels=chart_labels,
                           chart_reqs=chart_reqs,
                           chart_comps=chart_comps
                           )

@app.route('/schedule')
@login_required
def schedule():
    """Render the schedule/calendar page used for visualizing planned maintenance."""
    return render_template("schedule.html", page='schedule')

@app.route('/maintenance_requests', methods=['GET', 'POST'])
@login_required
def maintenance_requests():
    """
    Create (POST) and list (GET) maintenance requests.
    - POST: create new request from form fields and auto-assign team from equipment when possible.
    - GET: list requests optionally filtered by equipment_id query parameter.
    """
    # POST: create a new maintenance request
    if request.method == 'POST':
        description = request.form.get('description')
        equipment_id = request.form.get('equipment_id')
        priority = request.form.get('priority')  # Optional field for future use

        if description and equipment_id:
            eq = Equipment.query.get(equipment_id)
            new_req = MaintenanceRequest(
                description=description,
                equipment_id=equipment_id,
                team_id=eq.team_id if eq else None,
                created_by=current_user.id,
                status='new'
            )
            db.session.add(new_req)
            db.session.commit()
            flash('Maintenance Request created successfully!', 'success')
        else:
            flash('Error: Description and Equipment are required.', 'error')
            
        return redirect(url_for('maintenance_requests'))

    # GET: list requests, optionally filtered by equipment
    eq_id = request.args.get('equipment_id')
    if eq_id:
        reqs = MaintenanceRequest.query.filter_by(equipment_id=eq_id).order_by(MaintenanceRequest.created_at.desc()).all()
    else:
        reqs = MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).all()

    # Provide equipment list for the create form dropdown
    all_equipment = Equipment.query.all()

    return render_template("maintenance_requests.html", 
                           requests=reqs, 
                           equipment_list=all_equipment,
                           page='maintenance_requests')

# ------------------------
# Application startup
# ------------------------
if __name__ == '__main__':
    # Ensure database tables are created before serving requests
    with app.app_context():
        try:
            db.create_all()
            print("[SUCCESS] Database Connected.")
        except Exception as e:
            print(f"[ERROR] Connection Failed: {e}")
    app.run(debug=True)