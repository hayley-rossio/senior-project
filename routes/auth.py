# Imports from flask/flasks login, and the hashlib to hash passwords.
from flask import Blueprint, request, jsonify, session, render_template, redirect, flash, url_for
from flask_login import login_user, logout_user
import hashlib
# All of the backend connectors including my config file.
import mysql.connector
from config import DB_CONFIG
# Importing the user model.
from models.user import User
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')   # auth's blueprint creation.
def getDB():    # Getting access to the databases.
    return mysql.connector.connect(**DB_CONFIG)
def hashPass(password):     # Hashing the password.
    # !!! This may be a future update to something that doesn't compare a stored hash and a "rehash". !!!
    return hashlib.sha256(password.encode()).hexdigest()
@auth_bp.route('/register', methods=['GET', 'POST'])    # URL: /auth/register
def register():     # This does all of the registration backend.
    if request.method == 'GET':     # Loading the html page.
        return render_template('register.html')
    # Getting the inputs from the register.html form.
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # Checking for all boxes/inputs to be filled in.
    if not username or not email or not password:   # !! Change to a flash message. !!
        return jsonify({'error': 'Your username, email, and password are required.'}), 400 
    # Try to put them in the system, and if something goes wrong through an error.
    try:
        # Connection to the database.
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM RSPUsers WHERE username = %s OR email = %s", (username, email))  # Get the info.
        if cursor.fetchone():   # Block doubles of email's/username's so everything is unique in the database.
            flash('This email or username are already in use.')
        hashedPW = hashPass(password)   # Hash the inputed password so it's secure in the database.
        cursor.execute(     # Actually put the new user into the database.
            "INSERT INTO RSPUsers (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashedPW)
        )
        conn.commit()
        flash("You've successfully created an account! Please login.", 'success')  # New path to Login.
        return redirect(url_for('auth.loginPage'))
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@auth_bp.route('/login', methods=['POST'])  # URL: /auth/login
def login():    # All login information and redirects.
    # Get the information from the form.
    username = request.form.get('username')
    password = request.form.get('password')
    # If they submit and nothing is inputted.
    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    try:    # Attempt to log the user in.
        conn = getDB()
        cursor = conn.cursor(dictionary = True)
        cursor.execute("SELECT * FROM RSPUsers WHERE username = %s", (username,))
        user_row = cursor.fetchone()
        if user_row and user_row['password'] == hashPass(password):     # Check the login inputs and compare.
            user = User(user_row['id'], user_row['username'], user_row['email'])
            login_user(user)    # !!! Using login import !!!
        else:   # Redirect to the login page if their login attempt was invalid.
            flash('Invaild login.', 'danger')
            return redirect(url_for('auth.loginPage'))
        return redirect(url_for('main.home'))   # Redirect to the user's home page.
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@auth_bp.route('/login', methods=['GET'])
def loginPage():    # Reduces a code smell in redirecting to the login.html page.
    return render_template('login.html')
@auth_bp.route('/logout')   # URL: /auth/logout
def logout():   # Log's the user out.
    logout_user()       # !!! logout_user import !!!
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.loginPage'))