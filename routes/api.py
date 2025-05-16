from flask import Blueprint, request, jsonify, flash, redirect, url_for
import mysql.connector
from config import DB_CONFIG
from flask import current_app as app
from flask_login import login_required, current_user
from datetime import datetime, date
api_bp = Blueprint('api', __name__, url_prefix='/api')
def getDB():    # Getting access to the databases.
    return mysql.connector.connect(**DB_CONFIG)
@api_bp.route('/events', methods=['GET'])
@login_required
def getEvents():
    try:
        conn = getDB()
        cursor = conn.cursor(dictionary = True)
        cursor.execute(
            """ SELECT 
                RSPWorkouts.id, 
                RSPWorkouts.date AS start, 
                RSPWorkouts.type, 
                RSPWorkouts.duration, 
                RSPWorkouts.distance, 
                RSPWorkouts.equipment_id, 
                RSPEquipment.shoe, 
                RSPEquipment.id AS shoe_id
            FROM RSPWorkouts
            JOIN RSPEquipment ON RSPWorkouts.equipment_id = RSPEquipment.id
            WHERE RSPWorkouts.user_id = %s """,
            (current_user.id,)
        )
        rows = cursor.fetchall()
        events = []
        for row in rows:
            startDate = row['start'].isoformat()    # Formats the input for FullCalendar.
            title = f"{row['type']} - {row['duration']} min"
            if row['distance']:
                title += f", {row['distance']} mi"
            events.append({
                'id': row['id'],
                'title': title,
                'start': startDate,
                'extendedProps': {
                    'workoutID': row['id'],
                    'distance': row['distance'],
                    'shoe_name': row['shoe'],
                }
            })
        return jsonify(events)
    except Exception as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@api_bp.route('/add-workout', methods=['POST'])
@login_required
def addWorkout():
    data = request.form
    userID = current_user.id
    cursor = None
    conn = None
    try:
        wType = data.get('type')
        wDate = data.get('date')
        wDuration = data.get('duration')
        wDistance = float(data.get('distance') or 0)
        wNotes = data.get('notes')
        equipID = data.get('equipment_id') or None
        print(f"Distance: {wDistance}, Shoe: {equipID}")
        if not all ([wType, wDate, wDuration, wDistance]):
            flash('Please fill out all required fields.')
            return redirect(url_for('main.input'))
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO RSPWorkouts (user_id, date, type, duration, distance, notes, equipment_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (userID, wDate, wType, wDuration, wDistance, wNotes, equipID)
        )
        conn.commit()
        flash('Workout added successfully!', 'success')
        return redirect(url_for('main.home'))
    except Exception as err:
        flash(f'There was an error adding your workout: {str(err)}', 'error')
        return redirect(url_for('main.home'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@api_bp.route('/allraces', methods=['GET'])
@login_required
def getAllRaces():
    try:
        conn = getDB()
        cursor = conn.cursor(dictionary = True, buffered= True)
        cursor.execute(
            """ SELECT id, title, date 
            FROM RSPRaces 
            WHERE user_id = %s 
            ORDER BY date ASC """,
            (current_user.id,)
        )
        races = cursor.fetchall()
        upcomingraces = []
        pastraces = []
        today = datetime.today().date()
        for race in races:
            racedate = race['date']
            if racedate >= today:
                upcomingraces.append({
                    'id': race['id'],
                    'title': race['title'],
                    'date': race['date'].isoformat()
                })
            elif racedate < today:
                pastraces.append({
                    'id': race['id'],
                    'title': race['title'],
                    'date': race['date'].isoformat()
                })
            else:
                return jsonify({'message': 'No upcoming races', 'races': []}), 200
        cursor.execute(
            """ SELECT
                    WEEK(date, 1) AS weekNumber,
                    SUM(distance) AS totalMiles
                FROM RSPWorkouts
                WHERE user_id = %s
                    AND date >= CURDATE() - INTERVAL 5 WEEK
                GROUP BY weekNumber
                ORDER BY weekNumber DESC""",
            (current_user.id,)
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
        completionstats = cursor.fetchall()
        return jsonify({
                'upcomingraces': upcomingraces,
                'pastraces': pastraces,
                'weeklystats': weeklystats,
                'completionstats': completionstats
            })
    except Exception as err:
        print(f"[ERROR] /api/allraces: {err}")
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@api_bp.route('/nextrace', methods=['GET'])
@login_required
def getNextRace():
    try:
        conn = getDB()
        cursor = conn.cursor(dictionary = True, buffered= True)
        cursor.execute(
            """ SELECT title, date 
            FROM RSPRaces 
            WHERE user_id = %s 
            ORDER BY date ASC """,
            (current_user.id,)
        )
        races = cursor.fetchall()
        upcomingraces = []
        today = datetime.today().date()
        for race in races:
            racedate = race['date']
            if racedate >= today:
                upcomingraces.append({
                    'title': race['title'],
                    'date': race['date'].isoformat()
                })
            else:
                return jsonify({'message': 'No upcoming races', 'races': []}), 200
        return jsonify({
                'upcomingraces': upcomingraces,
            })
    except Exception as err:
        print(f"[ERROR] /api/nextrace: {err}")
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@api_bp.route('/deleterace/<int:race_id>', methods=['DELETE'])
@login_required
def deleteRace(race_id):
    try:
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute(
            """ DELETE FROM RSPRaces 
                WHERE id = %s AND user_id = %s """,
            (race_id, current_user.id)
        )
        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as err:
        print(f"[ERROR] /deleterace: {err}")
        return jsonify({'success': False, 'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@api_bp.route('/todaysworkout', methods = ['GET'])
@login_required
def todays():
    conn = getDB()
    cursor = conn.cursor(dictionary = True)
    cursor.execute(
        """ SELECT 
            RSPWorkouts.id, 
            RSPWorkouts.type, 
            RSPWorkouts.distance, 
            RSPWorkouts.duration, 
            RSPWorkouts.notes, 
            RSPWorkouts.equipment_id, 
            RSPWorkouts.complete, 
            RSPEquipment.shoe as shoe_name
        FROM RSPWorkouts
        JOIN RSPEquipment ON RSPWorkouts.equipment_id = RSPEquipment.id
        WHERE RSPWorkouts.user_id = %s AND RSPWorkouts.date = CURDATE() """,
        (current_user.id,)
    )
    workouts = cursor.fetchall()
    for workout in workouts:
        workout['isCompleted'] = workout['complete']
    cursor.close()
    conn.close()
    return jsonify(workouts)
@api_bp.route('/markComplete', methods=['POST'])
@login_required
def markCompleted():
    try:
        data = request.get_json()
        workout_id = data['workoutID']
        equipment_id = data['equipmentID']
        miles = float(data['distance'])
        if not all([workout_id, equipment_id, miles]):
            return jsonify({'error': 'Missing required fields'}), 400
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute(
            """ SELECT miles FROM RSPEquipment WHERE id = %s """,
            (equipment_id,)
        )
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'equipment not found'}), 404
        current_miles = result[0]
        print(f"cur: {current_miles}, miles: {miles}")
        new_miles = current_miles + float(miles)
        print(f"new: {new_miles}")
        cursor.execute(
            """ UPDATE RSPWorkouts SET complete = 1 WHERE id = %s""", 
            (workout_id,)
        )
        cursor.execute(
            """ UPDATE RSPEquipment SET miles = %s WHERE id = %s""", 
            (new_miles, equipment_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({
            'message': 'Workout marked as complete', 
            'newMiles': new_miles
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while marking the workout as complete'}), 500
@api_bp.route('/deleteWorkout', methods=['POST'])
@login_required
def deleteworkout():
    try:
        data = request.get_json()
        workout_id = data.get('workoutID')
        print(f"saw the back {workout_id}")
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute(
            """ SELECT equipment_id, distance, complete 
            FROM RSPWorkouts 
            WHERE id = %s """,
            (workout_id,)
        )
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'workout not found'}), 404
        equipment_id, distance, complete = result
        if complete and equipment_id and distance:
            cursor.execute(
                """ UPDATE RSPEquipment 
                SET miles = GREATEST(miles - %s, 0) 
                WHERE id = %s """,
                (distance, equipment_id)
            )
        cursor.execute(
            """ DELETE FROM RSPWorkouts 
                WHERE id = %s """,
            (workout_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'workout deleted'}), 200
    except Exception as err:
        print('error deleting workout', err)
        return jsonify({'error': str(err)}), 500