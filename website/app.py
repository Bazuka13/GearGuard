import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, Technician, Department, MaintenanceTeam, Equipment, MaintenanceRequest
from auth import auth_bp
from dotenv import load_dotenv
from sqlalchemy import func, desc, extract
import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hackathon_secret_key'

# 👇 YAHAN CHANGE KARO 👇
# Format: postgresql://USERNAME:PASSWORD@localhost/DATABASE_NAME
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/Gearguard' 
# (Yahan 'password' ki jagah apna asli password daalna mat bhulna!)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)

# --- MISSING ROOT ROUTE ---
@app.route('/')
def home():
    # Agar user login nahi hai, to Login page par bhejo
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    # Agar login hai, to Dashboard par
    return redirect(url_for('dashboard'))


# --- HELPER: GET CURRENT USER ---
def get_current_user():
    if 'user_id' not in session: return None
    if session.get('user_type') == 'technician':
        return Technician.query.get(session['user_id'])
    return User.query.get(session['user_id'])

# --- 1. DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    
    # Query Database based on your Schema's 'status' column
    new_reqs = MaintenanceRequest.query.filter_by(status='new').all()
    progress_reqs = MaintenanceRequest.query.filter_by(status='in_progress').all()
    repaired_reqs = MaintenanceRequest.query.filter_by(status='repaired').all()
    scrap_reqs = MaintenanceRequest.query.filter_by(status='scrap').all()
    
    total_open = len(new_reqs) + len(progress_reqs)
    
    return render_template('index.html', 
                         page='dashboard',
                         new_reqs=new_reqs,
                         progress_reqs=progress_reqs,
                         repaired_reqs=repaired_reqs,
                         scrap_reqs=scrap_reqs,
                         total_open=total_open)

# --- 2. API: UPDATE STAGE (Drag & Drop) ---
@app.route('/api/update_stage', methods=['POST'])
def update_stage():
    data = request.json
    task_id = data.get('task_id')
    # Convert 'New Request' text to 'new' status code if needed
    stage_map = {'New Request': 'new', 'In Progress': 'in_progress', 'Repaired': 'repaired', 'Scrap': 'scrap'}
    new_status = stage_map.get(data.get('new_stage'), data.get('new_stage').lower())
    
    req = MaintenanceRequest.query.get(task_id)
    if req:
        req.status = new_status
        
        # If a Technician drags to "In Progress", assign them automatically
        if new_status == 'in_progress' and session.get('user_type') == 'technician':
            req.technician_id = session['user_id']
            
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

# --- 3. CREATE REQUEST ---
@app.route('/create_request', methods=['POST'])
def create_request():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    
    equipment_id = request.form.get('equipment_id')
    equipment = Equipment.query.get(equipment_id)
    
    new_req = MaintenanceRequest(
        description=request.form.get('subject'), # Using subject input for description
        equipment_id=equipment.id,
        team_id=equipment.team_id, # Auto-assign Team from Equipment
        created_by=session['user_id'],
        status='new',
        duration_hours=float(request.form.get('duration', 0) or 0)
    )
    
    db.session.add(new_req)
    db.session.commit()
    
    flash('Request Created Successfully!', 'success')
    return redirect(url_for('dashboard'))

# --- 4. REQUESTS LIST ---
@app.route('/requests')
def maintenance_requests():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    
    search_query = request.args.get('q')
    if search_query:
        reqs = MaintenanceRequest.query.join(Equipment).filter(Equipment.name.ilike(f'%{search_query}%')).all()
    else:
        reqs = MaintenanceRequest.query.all()
        
    equipments = Equipment.query.all()
    return render_template('requests.html', page='requests', requests=reqs, equipments=equipments)

# --- 5. EQUIPMENT LIST ---
@app.route('/equipment')
def equipment():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    # Fetch all equipment
    all_equipment = Equipment.query.all()
    return render_template('equipment.html', page='equipment', equipment_list=all_equipment)

# --- 6. EQUIPMENT DETAIL ---
@app.route('/equipment/<int:id>')
def equipment_detail(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    eq = Equipment.query.get_or_404(id)
    
    # Calculate open requests count for the badge
    open_count = MaintenanceRequest.query.filter_by(equipment_id=eq.id, status='new').count()
    
    return render_template('equipment_detail.html', eq=eq, open_count=open_count)


# --- SEED DATA (To ensure Dropdowns work) ---
def seed_data():
    if not Department.query.first():
        d1 = Department(name='Production')
        d2 = Department(name='Logistics')
        db.session.add_all([d1, d2])
        
        t1 = MaintenanceTeam(name='Alpha Team')
        t2 = MaintenanceTeam(name='Beta Team')
        db.session.add_all([t1, t2])
        db.session.commit()
        
        # Add a dummy equipment
        e1 = Equipment(name='CNC Machine #3', serial_number='CNC-99', location='Building A', department_id=d1.id, team_id=t1.id)
        db.session.add(e1)
        db.session.commit()
        print("Database Seeded!")
        
@app.route('/schedule')
def schedule():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return render_template('schedule.html', page='schedule')

@app.route('/api/calendar-events')
def get_calendar_events():
    # Tumhare naye schema mein 'scheduled_date' nahi hai, isliye hum 'created_at' use kar rahe hain
    requests = MaintenanceRequest.query.all()
    events = []
    for req in requests:
        events.append({
            'id': req.id,
            'title': req.description,
            'date': req.created_at.strftime('%Y-%m-%d'), 
            'type': 'Corrective', # Default assumption
            'equipment': req.equipment.name
        })
    return jsonify(events)

# --- 8. TEAMS PAGE ---
@app.route('/teams')
def teams():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    # Fetch real teams from DB
    all_teams = MaintenanceTeam.query.all()
    return render_template('teams.html', page='teams', teams=all_teams)

# --- 9. WORK CENTERS ---
@app.route('/work_centers')
def work_centers():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    # Note: Tumhare naye schema mein 'WorkCenter' table nahi hai.
    # Isliye abhi ke liye hum empty list bhej rahe hain taaki error na aaye.
    return render_template('work_centers.html', page='work_centers', centers=[])

# --- 10. REPORTING ---
# --- 10. REPORTING (DYNAMIC ANALYTICS) ---
@app.route('/reporting')
def reporting():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    # 1. KPI Cards Data
    total_requests = MaintenanceRequest.query.count()
    completed_requests = MaintenanceRequest.query.filter_by(status='repaired').count()
    
    # Avg Duration Calculation
    avg_time_query = db.session.query(func.avg(MaintenanceRequest.duration_hours))\
        .filter(MaintenanceRequest.status == 'repaired').scalar()
    avg_time = round(avg_time_query, 1) if avg_time_query else 0.0

    # Critical Issues (Treating 'new' requests as critical backlog for now)
    critical_issues = MaintenanceRequest.query.filter_by(status='new').count()

    # 2. Top Equipment (Most Frequent Failures)
    top_equipment = db.session.query(
        Equipment.name, 
        func.count(MaintenanceRequest.id).label('count')
    ).join(MaintenanceRequest).group_by(Equipment.id).order_by(desc('count')).limit(5).all()

    # 3. Monthly Chart Data (Last 6 Months)
    today = datetime.datetime.today()
    chart_labels = []
    chart_reqs = []
    chart_comps = []

    for i in range(5, -1, -1):
        # Calculate date for previous months
        date_cursor = today - datetime.timedelta(days=i*30)
        month_num = date_cursor.month
        year_num = date_cursor.year
        month_name = date_cursor.strftime("%b") # Jan, Feb, etc.
        
        # Count for this specific month
        monthly_total = MaintenanceRequest.query.filter(
            extract('month', MaintenanceRequest.created_at) == month_num,
            extract('year', MaintenanceRequest.created_at) == year_num
        ).count()
        
        monthly_done = MaintenanceRequest.query.filter(
            extract('month', MaintenanceRequest.created_at) == month_num,
            extract('year', MaintenanceRequest.created_at) == year_num,
            MaintenanceRequest.status == 'repaired'
        ).count()

        chart_labels.append(month_name)
        chart_reqs.append(monthly_total)
        chart_comps.append(monthly_done)

    return render_template('reporting.html', 
                           page='reporting',
                           total=total_requests,
                           completed=completed_requests,
                           avg_time=avg_time,
                           critical=critical_issues,
                           top_eq=top_equipment,
                           chart_labels=chart_labels,
                           chart_reqs=chart_reqs,
                           chart_comps=chart_comps)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data() # Run once to populate tables
    app.run(debug=True)