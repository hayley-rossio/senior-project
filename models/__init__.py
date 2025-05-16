from flask_login import LoginManager
from models.user import User

login_manager = LoginManager()

@login_manager.user_loader
def loadUser(user_id):
    return User.getUserID(user_id)