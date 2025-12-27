from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Technician, Department

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # 1. Check if it's an Employee (User)
        user = User.query.filter_by(email=email).first()
        user_type = 'user'

        # 2. If not User, check if Technician
        if not user:
            user = Technician.query.filter_by(email=email).first()
            user_type = 'technician'

        if user and check_password_hash(user.password_hash, password):
            # Store ID and Type to distinguish in app.py
            session['user_id'] = user.id
            session['user_type'] = user_type 
            session['user_name'] = user.name
            session['user_role'] = 'Technician' if user_type == 'technician' else 'Employee'
            
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # Fetch Departments for the dropdown
    departments = Department.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department_id = request.form.get('department_id')

        # Check existing
        if User.query.filter_by(email=email).first() or Technician.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password)
        
        # Create Employee User
        new_user = User(
            name=name, 
            email=email, 
            password_hash=hashed_password, 
            department_id=department_id
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', departments=departments)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))