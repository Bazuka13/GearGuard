import os  # <--- Import OS
from flask import Flask, render_template, redirect, url_for, session
from models import db
from auth import auth_bp
from dotenv import load_dotenv  # <--- Import DotEnv

# Load variables from .env file
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION (Dynamic) ---

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INITIALIZE DB
db.init_app(app)

# REGISTER BLUEPRINT
app.register_blueprint(auth_bp)

# Inject current user info into all templates so templates can show actual user name and designation
@app.context_processor
def inject_current_user():
    return {
        'current_user_name': session.get('user_name'),
        'current_user_role': session.get('user_role') or session.get('user_designation')
    }

# --- PROTECTED ROUTES ---

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html', page='dashboard', user_name=session.get('user_name'))



@app.route('/schedule')
def schedule():
    return render_template('schedule.html', page='schedule')

@app.route('/requests')
def maintenance_requests():
    return render_template('requests.html', page='requests')

@app.route('/equipment')
def equipment():
    return render_template('equipment.html', page='equipment')

@app.route('/equipment/detail')
def equipment_detail():
    # Provide a list of equipments so the template's tojson has real data to serialize.
    # In a real app replace this with DB queries.
    equipment_list = [
        {'id': '1', 'name': 'CNC Machine #3', 'category': 'Machining', 'maintenance_team': 'Alpha Team', 'scrap_date': '2026-12-31'},
        {'id': '2', 'name': 'Conveyor Belt A', 'category': 'Logistics', 'maintenance_team': 'Beta Team', 'scrap_date': None},
        {'id': 'cnc', 'name': 'CNC Machine X', 'category': 'Machining', 'maintenance_team': 'Alpha Team', 'scrap_date': '2025-05-10'},
    ]

    # Optionally allow selecting an equipment by query param ?id=...
    eq_id = request.args.get('id')
    equipment = None
    if eq_id:
        equipment = next((e for e in equipment_list if str(e.get('id')) == str(eq_id)), None)

    return render_template('equipment_detail.html', page='equipment', equipment_list=equipment_list, equipment=equipment)

@app.route('/work_centers')
def work_centers():
    return render_template('work_centers.html', page='work_centers')

@app.route('/teams')
def teams():
    return render_template('teams.html', page='teams')

@app.route('/reporting')
def reporting():
    return render_template('reporting.html', page='reporting')

# --- API (Logic for Auto-fill) ---
@app.route('/api/get_team_info/<equipment_id>')
def get_team_info(equipment_id):
    # Dummy logic to simulate database
    if equipment_id == 'cnc':
        return jsonify({'team': 'Alpha Team (Machining)', 'lead': 'Mike Ross'})
    elif equipment_id == 'belt':
        return jsonify({'team': 'Beta Team (Logistics)', 'lead': 'John Smith'})
    return jsonify({'team': '', 'lead': ''})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)