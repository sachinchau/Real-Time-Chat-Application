from flask import Blueprint, render_template, request, redirect, url_for, flash

from flask_login import login_user, logout_user, login_required

from extensions import db, bcrypt

from models import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered!')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')

        return redirect(url_for('auth.login'))

    return render_template('register.html')
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):

            login_user(user)

            flash('Login successful!')

            return redirect(url_for('auth.dashboard'))

        flash('Invalid email or password!')

    return render_template('login.html')

@auth.route('/dashboard')
@login_required
def dashboard():

    return render_template('dashboard.html')

@auth.route('/logout')
@login_required
def logout():

    logout_user()

    flash('You have been logged out!')

    return redirect(url_for('auth.login'))