from flask import Flask

from config import Config
from models import User, Message, ChatRoom, RoomMember

from extensions import db, login_manager, socketio, bcrypt
from auth import auth
from chat import chat

app = Flask(__name__)

app.register_blueprint(auth)
app.register_blueprint(chat)
# Load configuration
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

login_manager.init_app(app)

bcrypt.init_app(app)

socketio.init_app(app, async_mode="threading")

# Login configuration
login_manager.login_view = "auth.login"

@app.route("/")
def home():
    return "Real-Time Chat Application is Running!"

with app.app_context():
    try:
        db.session.execute(db.text("SELECT 1"))
        print("MySQL Database Connected Successfully!")

    except Exception as e:
        print("Database Connection Failed:", e)

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == "__main__":
    socketio.run(
    app,
    debug=True,
    use_reloader=False,
    allow_unsafe_werkzeug=True
    )