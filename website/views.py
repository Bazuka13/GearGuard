from flask import Flask, render_template, request, redirect , url_for

app = Flask(__name__)

tasks = [
    {'id': 1, 'subject': 'Leaking Oil', 'status': 'New', 'equipment': 'CNC Machine'},
    {'id': 2, 'subject': 'Printer Jam', 'status': 'In Progress', 'equipment': 'Printer 01'},
    {'id': 3, 'subject': 'Routine Check', 'status': 'New', 'equipment': 'CNC Machine'}
]

equipment_data = {
    'CNC Machine': {'serial': 'SN-CNC-X99', 'location': 'Sector Alpha-1', 'is_scrap': False, 'specs': '5-Axis Milling'},
    'IT Server Rack': {'serial': 'SN-SRV-H02', 'location': 'Data Center B', 'is_scrap': False, 'specs': 'Xeon 32-Core'}
}

# Shared Tasks List
tasks = [
    {'id': 1, 'subject': 'Leaking Oil', 'status': 'New', 'equipment': 'CNC Machine', 'date': '2025-12-28', 'urgency': 'CRITICAL'}
]

# 1. The Route for the Dashboard (The Kanban View)
@app.route("/")
def index():
    # Adding priority and initials to make the UI pop 
    tasks = [
        {
            'id': 1, 
            'subject': 'Leaking Oil', 
            'status': 'New', 
            'equipment': 'CNC Machine', 
            'priority': 'High',
            'tech': 'JD'
        },
        {
            'id': 2, 
            'subject': 'Printer Jam', 
            'status': 'In Progress', 
            'equipment': 'Printer 01', 
            'priority': 'Medium',
            'tech': 'AL'
        },
        {
            'id': 3, 
            'subject': 'Calibration', 
            'status': 'Repaired', 
            'equipment': 'Staff Laptop', 
            'priority': 'Low',
            'tech': 'SS'
        }
    ]
    return render_template('index.html', tasks=tasks)
# 2. The Route to show the "Create Request" Form [cite: 39]
@app.route("/new-request", methods=['GET', 'POST'])
def new_request():
    if request.method == 'POST':
        # This is where you grab data from the HTML form
        subject = request.form.get('subject')
        # Here you would save to a database
        return redirect("/") # Go back to dashboard after saving
    
    return render_template('request.html')

def create_equipment():
    if request.method == 'POST':
        # Logic to save Equipment Name, Serial Number, and Location [cite: 16, 18]
        name = request.form.get('name')
        serial = request.form.get('serial')
        return redirect(url_for('index'))
    return render_template('equipment_form.html')

def create_request():
    # Mock data for the dropdown (usually from a database)
    equipment_list = ['CNC Machine', 'Printer 01', 'Staff Laptop']
    teams = ['Mechanics', 'Electricians', 'IT Support']

    if request.method == 'POST':
        # 1. Grab data from the form (Flow 1: The Breakdown)
        subject = request.form.get('subject') # e.g. "Leaking Oil" 
        equipment = request.form.get('equipment') # 
        request_type = request.form.get('type') # Corrective vs Preventive [cite: 27]
        
        # 2. Logic: In Odoo/Flask, we'd save this to a database here
        print(f"New Request Created: {subject} for {equipment}")
        
        # 3. Redirect back to the Kanban dashboard [cite: 53]
        return redirect(url_for('index'))

    return render_template('request_form.html', equipment=equipment_list, teams=teams)

def maintenance_calendar():
    # Mock data for Preventive requests [cite: 29, 62]
    planned_events = [
        {
            'date': '2025-12-28', 
            'task': 'CNC_SYSTEM_RECALIBRATION', 
            'asset': 'CNC Machine', 
            'tech': 'John Doe',
            'urgency': 'CRITICAL'
        },
        {
            'date': '2025-12-30', 
            'task': 'SERVER_THERMAL_OPTIMIZATION', 
            'asset': 'IT Server Rack', 
            'tech': 'Ada Lovelace',
            'urgency': 'ROUTINE'
        }
    ]
    return render_template('calendar.html', events=planned_events)

@app.route('/equipment/<name>')
def equipment_detail(name):
    equipment = equipment_data.get(name)
    count = len([t for t in tasks if t['equipment'] == name])
    return render_template('equipment_detail.html', equipment=equipment, name=name, count=count)

@app.route('/equipment/<name>/scrap')
def mark_scrap(name):
    # This is the fix for the Scrap Button
    if name in equipment_data:
        equipment_data[name]['is_scrap'] = True
    return redirect(url_for('equipment_detail', name=name))

def maintenance_teams():
    # Adding role and avatar initials for a premium look
    teams = [
        {'name': 'Mechanics', 'icon': '🛠️', 'members': [
            {'name': 'John Doe', 'role': 'Lead Technician', 'initials': 'JD'},
            {'name': 'Mike Ross', 'role': 'Hydraulics Expert', 'initials': 'MR'}
        ]},
        {'name': 'Electricians', 'icon': '⚡', 'members': [
            {'name': 'Sarah Sparks', 'role': 'Master Electrician', 'initials': 'SS'},
            {'name': 'Tom Volt', 'role': 'Systems Specialist', 'initials': 'TV'}
        ]},
        {'name': 'IT Support', 'icon': '💻', 'members': [
            {'name': 'Alan Turing', 'role': 'Network Admin', 'initials': 'AT'},
            {'name': 'Ada Lovelace', 'role': 'Software Support', 'initials': 'AL'}
        ]}
    ]
    return render_template('teams.html', teams=teams)

from flask import request, redirect, url_for

@app.route("/calendar/add", methods=['POST'])
def add_calendar_entry():
    # In a real app, you would save this to your Database [cite: 47, 48]
    task = request.form.get('task')
    asset = request.form.get('asset')
    date = request.form.get('date')
    
    print(f"New Preventive Task Initialized: {task} for {asset} on {date}")
    
    # After saving, return to the schedule
    return redirect(url_for('maintenance_calendar'))

if __name__ == "__main__":
    app.run(debug=True)