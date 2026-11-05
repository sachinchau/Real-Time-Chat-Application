from extensions import db,login_manager
from flask_login import UserMixin

class User(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    last_seen = db.Column(db.DateTime, nullable=True)



@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))

class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    content = db.Column(db.Text, nullable=False)

    room_id = db.Column(
    db.Integer,
    db.ForeignKey('chat_room.id'),
    nullable=True
    )

    timestamp = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )
    is_delivered = db.Column(db.Boolean, default=False, nullable=False)

    is_read = db.Column(db.Boolean, default=False, nullable=False)

class ChatRoom(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    room_name = db.Column(db.String(100), nullable=False)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
class RoomMember(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    room_id = db.Column(
        db.Integer,
        db.ForeignKey('chat_room.id'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint('room_id', 'user_id'),
    )