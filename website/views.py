from flask import Flask, render_template, request, redirect , url_for

app = Flask(__name__)

# 1. The Route for the Dashboard (The Kanban View)
@app.route("/")
def index():
    # In a real app, this comes from a database. 
    # For now, we use a list of "Maintenance Requests" [cite: 25]
    mock_requests = [
        {'id': 1, 'subject': 'Printer Jam', 'status': 'New', 'equipment': 'Printer 01'},
        {'id': 2, 'subject': 'Leaking Oil', 'status': 'In Progress', 'equipment': 'CNC Machine'}
    ]
    return render_template('index.html', tasks=mock_requests)

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

if __name__ == "__main__":
    app.run(debug=True)