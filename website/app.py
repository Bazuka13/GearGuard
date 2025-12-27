from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# --- ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('index.html', page='dashboard')

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
    app.run(debug=True)