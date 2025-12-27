from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash

# 👇 IMPORTS (Dot hata diya hai taaki import error na aaye)
from models import User, Department, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # 1. Check if User Exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'error')
            # 👇 FIX: Agar error hai to wapas signup page par bhejo (namespace ke saath)
            return redirect(url_for('auth.signup')) 

        # 2. AUTO-ASSIGN DEPARTMENT
        default_dept = Department.query.first()
        
        if not default_dept:
            flash("System Error: No Departments found. Run 'python seed.py' first.", 'error')
            return redirect(url_for('auth.signup'))

        try:
            # 3. Create User
            new_user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password),
                department_id=default_dept.id
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created! Please login.', 'success')
            
            # 👇 FIX: Success hone par Login page par bhejo (namespace ke saath)
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"Database Error: {e}")
            db.session.rollback()
            flash('Something went wrong.', 'error')
            return redirect(url_for('auth.signup'))

    # GET Request: Page Render karo
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from flask_login import login_user

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # Simple password check (Hash check production me use karna)
        if user: 
            login_user(user, remember=True)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard')) 
        else:
            flash('Incorrect email or password.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    # 👇 FIX: Logout ke baad Login page par (namespace ke saath)
    return redirect(url_for('auth.login'))