from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from config import DB_CONFIG
import mysql.connector
from models.user import User
main_bp = Blueprint('main', __name__)
def getDB():    # Getting access to the databases.
    return mysql.connector.connect(**DB_CONFIG)
# Redirect to the home.html page.
@main_bp.route('/home')
@login_required
def home():
    return render_template('home.html')
@main_bp.route('/input')
@login_required
def input():
    conn = getDB()
    cursor = conn.cursor(dictionary = True)
    cursor.execute(
        """SELECT id, brand, shoe FROM RSPEquipment WHERE user_id = %s AND retired = 0""",
        (current_user.id,)
    )
    shoes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('workout.html', shoes=shoes)
@main_bp.route('/profile')
@login_required
def profile():
    try:
        conn = getDB()
        cursor = conn.cursor(dictionary = True)
        cursor.execute(     # Monthly stats
            """ SELECT COUNT(*) AS totalWorkouts, 
                SUM(distance) AS totalMile
                FROM RSPWorkouts
                WHERE user_id = %s
                AND MONTH(date) = MONTH(CURRENT_DATE())
                AND YEAR(date) = YEAR(CURRENT_DATE()) """, 
            (current_user.id,)
        )
        stats = cursor.fetchone()
        cursor.execute(     # all races ordered by date
            """ SELECT id, title, date
                FROM RSPRaces
                WHERE user_id = %s
                ORDER BY date ASC """,
            (current_user.id,)
        )
        races = cursor.fetchall()
        cursor.execute(     # weekly stats - month
            """ SELECT 
                    WEEK(date, 1) AS weekNumber,
                    SUM(distance) AS totalMiles
                FROM RSPWorkouts
                WHERE user_id = %s
                AND MONTH(date) = MONTH(CURRENT_DATE())
                AND YEAR(date) = YEAR(CURRENT_DATE())
                GROUP BY weekNumber
                ORDER BY weekNumber """,
            (current_user.id, )
        )
        weeklystats = cursor.fetchall()
        cursor.execute(
            """ SELECT
                    SUM(CASE WHEN complete = TRUE THEN 1 ELSE 0 END) AS completecount,
                    COUNT(*) AS totalcount
                FROM RSPWorkouts
                WHERE user_id = %s
                    AND MONTH(date) = MONTH(CURRENT_DATE())
                    AND YEAR(date) = YEAR(CURRENT_DATE())""",
            (current_user.id,)
        )
        completionstats = cursor.fetchone()
        return render_template(
            'profile.html', 
            stats = stats,
            races = races,
            weeklystats = weeklystats,
            completionstats = completionstats
        )
    finally:
        cursor.close()
        conn.close()
@main_bp.route('/addrace', methods=['POST'])
@login_required
def addrace():
    title = request.form.get('title')
    date = request.form.get('date')
    if not title or not date:
        flash('Both title and date are required.', 'error')
        return login_required(url_for('main.profile'))
    try:
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute(
            """ INSERT INTO RSPRaces (user_id, title, date) VALUES (%s, %s, %s) """,
            (current_user.id, title, date)
        )
        conn.commit()
        flash("Race added successfully!", 'success')
    except Exception as err:
        flash(f"Error adding race: {err}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('main.profile'))
@main_bp.route('/equipment', methods=['GET', 'POST'])
@login_required
def equipment():
    conn = getDB()
    cursor = conn.cursor(dictionary = True)
    if request.method == 'POST':
        shoe = request.form.get('shoe')
        brand = request.form.get('brand')
        model = request.form.get('model')
        try:
            miles = float(request.form.get('miles') or 0)
        except ValueError:
            miles = 0.0
        cursor.execute(
            """ INSERT INTO RSPEquipment (user_id, shoe, brand, miles, model) 
                VALUES (%s, %s, %s, %s, %s) """,
            (current_user.id, shoe, brand, miles, model,)
        )
        conn.commit()
    cursor.execute(
        """ SELECT shoe, brand, miles, retired, model 
            FROM RSPEquipment 
            WHERE user_id = %s """,
        (current_user.id,)
    )
    equipment = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('equipment.html', equipment=equipment)
# Test code to ensure the databases were working.
# Outdated/Can be commented out as it's only used in debugging the databases.
@main_bp.route('/db-tester')
def db_tester():
    return render_template('db_tester.html')
