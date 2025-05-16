from flask_login import UserMixin
import mysql.connector
from config import DB_CONFIG    # My config file for the databases.

# Connecting to the databases through a config file.
def getDB():
    return mysql.connector.connect(**DB_CONFIG)

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = str(id)
        self.username = username
        self.email = email
        
    @staticmethod
    def getUserID(user_id):
        conn = getDB()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM RSPUsers WHERE id = %s", (user_id,))
        user_row = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_row:
            return User(user_row['id'], user_row['username'], user_row['email'])
        return None