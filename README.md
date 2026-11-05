# Real-Time Chat Application

A real-time messaging web application built using **Python, Flask, Flask-SocketIO, and MySQL**. It allows users to create accounts, communicate privately, create group chat rooms, and exchange messages instantly using WebSocket technology.

## Features

- **User Authentication:** User registration and login with secure password hashing.
- **Private Chat:** One-to-one messaging between registered users.
- **Group Chat Rooms:** Create and participate in group conversations.
- **Room Management:** Room creators can add new members to their rooms.
- **Real-Time Messaging:** Exchange messages instantly using Flask-SocketIO and WebSockets.
- **Message History:** Store messages in MySQL for persistent conversations.
- **Online Status:** Display users' online/offline status.
- **Typing Indicator:** Show when another user is typing.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| Flask-SocketIO | Real-time communication |
| Socket.IO / WebSocket | Instant messaging |
| MySQL | Database |
| Flask-SQLAlchemy | Database ORM |
| Flask-Login | User authentication |
| Flask-Bcrypt | Password hashing |
| HTML, CSS, Bootstrap 5 | Frontend |

## Project Structure

```text
Real Time/
│
├── app.py
├── auth.py
├── chat.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── chat_users.html
│   ├── chat.html
│   ├── chat_rooms.html
│   ├── create_room.html
│   ├── group_chat.html
│   └── add_member.html
│
└── static/
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "Real Time"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

- Install and start MySQL.
- Create a database for the application.
- Configure your database connection and secret key in a `.env` file.

Example:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://username:password@localhost/database_name
```

Replace the example values with your own configuration.

### 5. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## How It Works

1. Register a new account or log in.
2. Open the user list to start a private conversation.
3. Create a group chat room or join a room you belong to.
4. The room creator can add other registered users.
5. Send messages and receive them instantly through WebSocket communication.

## Learning Outcomes

Through this project, I gained practical experience with:

- Building web applications using Flask.
- Implementing real-time communication using WebSockets.
- Managing private and group conversations.
- Designing relational database models using MySQL.
- Implementing authentication and password hashing.
- Working with Flask-SocketIO events and room management.

## Author

**Sachin Kumar**

GitHub: [sachinchau](https://github.com/sachinchau)

LinkedIn: [Sachin Kumar](https://www.linkedin.com/in/sachin-kumar-ab728b318/)