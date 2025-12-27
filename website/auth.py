from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User 

# Create the Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # name
            session['user_id'] = user.id
            session['user_name'] = getattr(user, 'name', '')

            # designation/role: support either field name on the model
            session['user_role'] = getattr(user, 'role', None) or getattr(user, 'designation', '') 

            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Check if email exists
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('auth.signup'))

        # Create new user with hashed password
        # FIX: Removed "method='sha256'". Werkzeug will now use the default secure method (scrypt).
        hashed_password = generate_password_hash(password) 
        
        new_user = User(name=name, email=email, password_hash=hashed_password, role=role)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))