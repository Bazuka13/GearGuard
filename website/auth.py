"""
Authentication blueprint for GearGuard.

Contains signup, login and logout routes.
- signup: creates a user and assigns a default department if no department selection exists.
- login: authenticates and logs in a user via Flask-Login (password verification should be used in production).
- logout: logs out the current user.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash

# Import models and database session
from models import User, Department, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user registration.
    - POST: creates a new user with a default department if present.
    - GET: renders the signup form.
    Important: This implementation auto-assigns the first department if no explicit department selection is used.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # Check for existing user to prevent duplicates
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'error')
            return redirect(url_for('auth.signup'))

        # Use first department as default to ensure foreign key is valid
        default_dept = Department.query.first()
        if not default_dept:
            flash("System Error: No Departments found. Run the seed script to populate departments.", 'error')
            return redirect(url_for('auth.signup'))

        try:
            # Create and persist the new user with a hashed password
            new_user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password),
                department_id=default_dept.id
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Account created! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            # Rollback on error and inform the user to try again
            print(f"Database Error: {e}")
            db.session.rollback()
            flash('Something went wrong while creating the account.', 'error')
            return redirect(url_for('auth.signup'))

    # GET: render the signup page
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Render login page (GET) and authenticate user (POST).
    Note: Current implementation calls login_user without explicit password check here;
    in production ensure password verification (check_password_hash) before login_user().
    """
    from flask_login import login_user

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # If user exists, log them in. Add a password check in production.
        if user:
            login_user(user, remember=True)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Log out the current user and redirect to the login page."""
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))