from flask import Flask, jsonify, redirect, url_for, render_template
import mysql.connector
from config import DB_CONFIG
from flask_login import LoginManager, current_user
from routes.auth import auth_bp
from routes.main import main_bp
from routes.api import api_bp
from models.user import User    # Moved from auth.py to avoid a circular import.
app = Flask(__name__)
app.secret_key = 'MitchellMaxOli'
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
def testDBConn():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"MySQL connection success! Version: {version[0]}"
    except mysql.connector.Error as err:
        return f"Error: {err}"
@app.route('/')
def startup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('register.html')
@app.route('/test-db')
def testDB():
    result = testDBConn()
    return jsonify({'db_status': result})
# Copied from auth.py to ensure loadUser works.
def getDB():
    return mysql.connector.connect(**DB_CONFIG)
# Moved from auth.py to avoid a circular import.
@login_manager.user_loader
def loadUser(user_id):
    conn = getDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM RSPUsers WHERE id = %s", (user_id, ))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'])
    return None
if __name__ == '__main__':
    app.run(debug=True, port=4356)