from flask import Flask
import views

app = Flask(__name__)

# 1. Dashboard / Kanban Route
app.add_url_rule('/', 'index', views.index)

# 2. Report Issue (Breakdown Flow)
app.add_url_rule('/new-request', 'new_request', views.new_request, methods=['GET', 'POST'])

# 3. Equipment Detail (Smart Button Page)
app.add_url_rule('/equipment/<name>', 'equipment_detail', views.equipment_detail)

# 4. Maintenance Units (Teams Page)
app.add_url_rule('/teams', 'maintenance_teams', views.maintenance_teams)

# 5. Operational Schedule (Calendar View)
app.add_url_rule('/calendar', 'maintenance_calendar', views.maintenance_calendar)

# 6. NEW: Add Entry Logic (Handles the Modal Form)
app.add_url_rule('/calendar/add', 'add_calendar_entry', views.add_calendar_entry, methods=['POST'])

if __name__ == "__main__":
    app.run(debug=True, port=5000)