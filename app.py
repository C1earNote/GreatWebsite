import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app)

# Configure SocketIO
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbdbase_user:w82vkLMjw6Q4UoApnlzIjtCCCwIku0c9@dpg-ctjebsd2ng1s73bj0e70-a.oregon-postgres.render.com/dbdbase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database tables
with app.app_context():
    db.create_all()

# Register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    # Use SQLAlchemy query
    user = User.query.filter_by(username=username).first()
    if not user or not checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200

# Send Message Endpoint
@app.route('/messages', methods=['POST'])
def send_message():
    data = request.json

    sender_username = data.get('sender')
    receiver_username = data.get('receiver')
    content = data.get('content')

    if not sender_username or not receiver_username or not content:
        return jsonify({"message": "Sender, receiver, and content are required"}), 400

    sender = User.query.filter_by(username=sender_username).first()
    receiver = User.query.filter_by(username=receiver_username).first()

    if not sender or not receiver:
        return jsonify({"message": "Sender or receiver not found"}), 404

    new_message = Message(sender_id=sender.id, receiver_id=receiver.id, content=content)
    db.session.add(new_message)
    db.session.commit()

    message_data = {
        'sender': sender.username,
        'receiver': receiver.username,
        'content': content,
        'timestamp': new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }
    socketio.emit('new_message', message_data)
    print("Message emitted to frontend: ", message_data)  # Log message emission

    return jsonify({"message": "Message sent successfully"}), 201

# Get Messages Endpoint
@app.route('/messages/<username>', methods=['GET'])
def get_messages(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    received_messages = Message.query.filter_by(receiver_id=user.id).all()
    sent_messages = Message.query.filter_by(sender_id=user.id).all()

    received = [{"sender": User.query.get(msg.sender_id).username, 
                 "content": msg.content, 
                 "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for msg in received_messages]
    sent = [{"receiver": User.query.get(msg.receiver_id).username, 
             "content": msg.content, 
             "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for msg in sent_messages]

    return jsonify({"received": received, "sent": sent}), 200

# SocketIO connection handler
@socketio.on('connect')
def handle_connect():
    print("A client connected.")

@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected.")

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
