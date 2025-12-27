from flask import Flask
import views
app = Flask(__name__)

# This connects the URL '/' to the index function in views.py
app.add_url_rule('/', 'index', views.index)

# This connects '/add-equipment' to the equipment function
app.add_url_rule('/add-equipment', 'create_equipment', views.create_equipment, methods=['GET', 'POST'])

app.add_url_rule('/new-request', 'create_request', views.create_request, methods=['GET', 'POST'])

if __name__ == "__main__":
    # debug=True allows the server to auto-restart when you save a file
    app.run(debug=True, port=5000)