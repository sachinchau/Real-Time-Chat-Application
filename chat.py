from flask import Blueprint, render_template, abort,request
from sqlalchemy import or_, and_
from datetime import datetime
from flask_login import login_required, current_user
from flask_socketio import emit, join_room,rooms
from extensions import socketio, db
from models import User, Message, ChatRoom, RoomMember


# Store connected users and their Socket.IO session IDs
online_users = {}

chat = Blueprint('chat', __name__)

def get_private_room(user1_id, user2_id):
    first = min(user1_id, user2_id)
    second = max(user1_id, user2_id)

    return f"private_{first}_{second}"

@socketio.on('join_private')
def handle_join_private(data):

    if not current_user.is_authenticated:
        emit('chat_error', {'message': 'Please log in.'})
        return

    try:
        recipient_id = int(data.get('recipient_id'))
    except (TypeError, ValueError):
        emit('chat_error', {'message': 'Invalid recipient.'})
        return

    recipient = db.session.get(User, recipient_id)

    if not recipient or recipient.id == current_user.id:
        emit('chat_error', {'message': 'Invalid recipient.'})
        return

    room = get_private_room(current_user.id, recipient.id)

    join_room(room)

    emit('joined_private', {'room': room})

@socketio.on('send_private_message')
def handle_private_message(data):

    if not current_user.is_authenticated:
        emit('chat_error', {'message': 'Please log in.'})
        return

    try:
        recipient_id = int(data.get('recipient_id'))
    except (TypeError, ValueError):
        emit('chat_error', {'message': 'Invalid recipient.'})
        return

    recipient = db.session.get(User, recipient_id)

    if not recipient or recipient.id == current_user.id:
        emit('chat_error', {'message': 'Invalid recipient.'})
        return

    content = data.get('content', '')

    if not isinstance(content, str):
        emit('chat_error', {'message': 'Invalid message.'})
        return

    content = content.strip()

    if not content or len(content) > 5000:
        emit('chat_error', {'message': 'Message must contain 1–5000 characters.'})
        return

    room = get_private_room(current_user.id, recipient.id)

    # Ensure sender has joined this conversation
    from flask_socketio import rooms

    if room not in rooms():
        emit('chat_error', {'message': 'Join the conversation first.'})
        return

    new_message = Message(
        sender_id=current_user.id,
        receiver_id=recipient.id,
        content=content
    )

    db.session.add(new_message)
    db.session.commit()

    message_data = {
        'message_id': new_message.id,
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'content': content,
        'timestamp': new_message.timestamp.isoformat()

    }

    emit(
    'receive_message',
    message_data,
    to=f"user_{recipient.id}"
    )
        # Send a copy to the sender's current browser
    emit(
        'receive_message',
        message_data,
        to=request.sid
    )



@chat.route('/chat')
@login_required
def chat_users():
    users = User.query.filter(User.id != current_user.id).all()

    online_user_ids = list(online_users.keys())

    return render_template(
        'chat_users.html',
        users=users,
        online_user_ids=online_user_ids
    )

@chat.route('/chat/<int:user_id>')
@login_required
def private_chat(user_id):

    recipient = User.query.get_or_404(user_id)

    if recipient.id == current_user.id:
        abort(400)

    # Fetch previous messages between these two users
    messages = Message.query.filter(
        or_(
            and_(
                Message.sender_id == current_user.id,
                Message.receiver_id == recipient.id
            ),
            and_(
                Message.sender_id == recipient.id,
                Message.receiver_id == current_user.id
            )
        )
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        'chat.html',
        recipient=recipient,
        messages=messages
    )

@socketio.on('connect')
def handle_connect(auth=None):

    if not current_user.is_authenticated:
        return False

    user_id = current_user.id

    # Join the user's personal room
    join_room(f"user_{user_id}")

    online_users.setdefault(user_id, set()).add(request.sid)

    print(f"User {user_id} is online")

    emit(
        'user_status',
        {
            'user_id': user_id,
            'status': 'online'
        },
        broadcast=True
    )

@socketio.on('disconnect')
def handle_disconnect(reason=None):

    if not current_user.is_authenticated:
        return

    user_id = current_user.id

    user_sessions = online_users.get(user_id)

    if user_sessions:
        user_sessions.discard(request.sid)

        # Update last seen only when the user has no active sessions
        if not user_sessions:
            online_users.pop(user_id, None)

            user = db.session.get(User, user_id)

            if user:
                user.last_seen = datetime.now()
                db.session.commit()

            print(f"User {user_id} is offline")

            emit(
                'user_status',
                {
                    'user_id': user_id,
                    'status': 'offline',
                    'last_seen': user.last_seen.strftime('%I:%M %p') if user and user.last_seen else None
                },
                broadcast=True
            )

@socketio.on('typing')
def handle_typing(data):
    if not current_user.is_authenticated:
        return

    recipient_id = data.get('recipient_id')

    if not recipient_id:
        return

    recipient = db.session.get(User, recipient_id)

    if not recipient or recipient.id == current_user.id:
        return

    room = get_private_room(current_user.id, recipient.id)

    if room not in rooms():
        return

    emit(
        'user_typing',
        {'username': current_user.username},
        to=room,
        include_self=False
    )


@socketio.on('stop_typing')
def handle_stop_typing(data):
    if not current_user.is_authenticated:
        return

    recipient_id = data.get('recipient_id')

    if not recipient_id:
        return

    recipient = db.session.get(User, recipient_id)

    if not recipient or recipient.id == current_user.id:
        return

    room = get_private_room(current_user.id, recipient.id)

    if room not in rooms():
        return

    emit(
        'user_stop_typing',
        to=room,
        include_self=False
    )

@socketio.on('message_delivered')
def handle_message_delivered(data):

    if not current_user.is_authenticated:
        return

    try:
        message_id = int(data.get('message_id'))
    except (TypeError, ValueError):
        return

    message = db.session.get(Message, message_id)

    if not message:
        return

    # Only the intended recipient can acknowledge delivery
    if message.receiver_id != current_user.id:
        return

    if not message.is_delivered:
        message.is_delivered = True
        db.session.commit()

    # Notify the original sender
    emit(
        'message_status',
        {
            'message_id': message.id,
            'status': 'delivered'
        },
        to=f"user_{message.sender_id}"
    )

@socketio.on('mark_messages_read')
def handle_mark_messages_read(data):

    if not current_user.is_authenticated:
        return

    try:
        recipient_id = int(data.get('recipient_id'))
    except (TypeError, ValueError):
        return

    recipient = db.session.get(User, recipient_id)

    if not recipient or recipient.id == current_user.id:
        return

    room = get_private_room(current_user.id, recipient.id)

    if room not in rooms():
        return

    unread_messages = Message.query.filter(
        Message.sender_id == recipient.id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).all()

    for message in unread_messages:
        message.is_read = True
        message.is_delivered = True

    db.session.commit()

    for message in unread_messages:
        emit(
            'message_status',
            {
                'message_id': message.id,
                'status': 'read'
            },
            to=f"user_{message.sender_id}"
        )
@chat.route('/create-room', methods=['GET', 'POST'])
@login_required
def create_room():

    if request.method == 'POST':

        room_name = request.form.get('room_name', '').strip()

        if not room_name:
            return "Room name is required"

        new_room = ChatRoom(
            room_name=room_name,
            created_by=current_user.id
        )

        db.session.add(new_room)
        db.session.commit()

        # Add creator as the first room member
        member = RoomMember(
            room_id=new_room.id,
            user_id=current_user.id
        )

        db.session.add(member)
        db.session.commit()

        return "Room created successfully!"

    return render_template('create_room.html')

@chat.route('/room/<int:room_id>/add-member', methods=['GET', 'POST'])
@login_required
def add_room_member(room_id):

    room = ChatRoom.query.get_or_404(room_id)

    # Only the room creator can add members
    if room.created_by != current_user.id:
        abort(403)

    # Get users who are not already members
    existing_member_ids = db.session.query(
        RoomMember.user_id
    ).filter_by(room_id=room.id).subquery()

    available_users = User.query.filter(
        ~User.id.in_(existing_member_ids),
        User.id != current_user.id
    ).all()

    if request.method == 'POST':

        try:
            user_id = int(request.form.get('user_id'))
        except (TypeError, ValueError):
            abort(400)

        user = db.session.get(User, user_id)

        if not user:
            abort(404)

        existing_member = RoomMember.query.filter_by(
            room_id=room.id,
            user_id=user.id
        ).first()

        if existing_member:
            return "User is already a member."

        member = RoomMember(
            room_id=room.id,
            user_id=user.id
        )

        db.session.add(member)
        db.session.commit()

        return "Member added successfully!"

    return render_template(
        'add_member.html',
        room=room,
        users=available_users
    )

@chat.route('/rooms')
@login_required
def chat_rooms():

    rooms_list = ChatRoom.query.join(
        RoomMember,
        ChatRoom.id == RoomMember.room_id
    ).filter(
        RoomMember.user_id == current_user.id
    ).all()

    return render_template(
        'chat_rooms.html',
        rooms=rooms_list
    )
@chat.route('/room/<int:room_id>')
@login_required
def group_chat(room_id):

    room = ChatRoom.query.get_or_404(room_id)

    # Only existing members can access the room
    membership = RoomMember.query.filter_by(
        room_id=room.id,
        user_id=current_user.id
    ).first()

    if not membership:
        abort(403)

    messages = Message.query.filter_by(
        room_id=room.id
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        'group_chat.html',
        room=room,
        messages=messages
    )
@socketio.on('join_group')
def handle_join_group(data):

    if not current_user.is_authenticated:
        return

    try:
        room_id = int(data.get('room_id'))
    except (TypeError, ValueError):
        return

    room = db.session.get(ChatRoom, room_id)

    if not room:
        return

    membership = RoomMember.query.filter_by(
        room_id=room_id,
        user_id=current_user.id
    ).first()

    if not membership:
        return

    join_room(f"group_{room_id}")

    emit('joined_group', {
        'room_name': room.room_name
    })
@socketio.on('send_group_message')
def handle_group_message(data):

    if not current_user.is_authenticated:
        return

    try:
        room_id = int(data.get('room_id'))
    except (TypeError, ValueError):
        return

    content = data.get('content', '')

    if not isinstance(content, str):
        return

    content = content.strip()

    if not content or len(content) > 5000:
        return

    membership = RoomMember.query.filter_by(
        room_id=room_id,
        user_id=current_user.id
    ).first()

    if not membership:
        return

    room_name = f"group_{room_id}"

    if room_name not in rooms():
        return

    new_message = Message(
        sender_id=current_user.id,
        receiver_id=None,
        room_id=room_id,
        content=content
    )

    db.session.add(new_message)
    db.session.commit()

    emit('receive_group_message', {
        'message_id': new_message.id,
        'sender_name': current_user.username,
        'content': content
    }, to=room_name)