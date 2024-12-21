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

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

# Create the database tables (Only needed once)
with app.app_context():
    db.create_all()

# Register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Ensure username and password are provided
    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    # Hash the password and save user
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    # Ensure username and password are provided
    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    # Retrieve user from database
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    # Verify password
    if checkpw(password.encode('utf-8'), user.password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

# Send Message Endpoint
@app.route('/messages', methods=['POST'])
def send_message():
    data = request.json

    # Ensure sender, receiver, and content are provided
    sender_username = data.get('sender')
    receiver_username = data.get('receiver')
    content = data.get('content')

    if not sender_username or not receiver_username or not content:
        return jsonify({"message": "Sender, receiver, and content are required"}), 400

    # Validate sender and receiver existence
    sender = User.query.filter_by(username=sender_username).first()
    receiver = User.query.filter_by(username=receiver_username).first()

    if not sender:
        return jsonify({"message": f"Sender '{sender_username}' not found"}), 404
    if not receiver:
        return jsonify({"message": f"Receiver '{receiver_username}' not found"}), 404

    # Save the message
    try:
        new_message = Message(sender_id=sender.id, receiver_id=receiver.id, content=content)
        db.session.add(new_message)
        db.session.commit()

        # Emit the new message to connected clients
        message_data = {
            "sender": sender.username,
            "receiver": receiver.username,
            "content": content,
            "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        socketio.emit('new_message', message_data)

        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        return jsonify({"message": f"Error sending message: {str(e)}"}), 500

# Get Messages Endpoint
@app.route('/messages/<username>', methods=['GET'])
def get_messages(username):
    # Retrieve the user from the database
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Get all messages sent and received by the user
    received_messages = Message.query.filter_by(receiver_id=user.id).all()
    sent_messages = Message.query.filter_by(sender_id=user.id).all()

    # Format messages for the response
    received = [{"sender": msg.sender.username, "content": msg.content, "timestamp": msg.timestamp} for msg in received_messages]
    sent = [{"receiver": msg.receiver.username, "content": msg.content, "timestamp": msg.timestamp} for msg in sent_messages]

    return jsonify({"received": received, "sent": sent}), 200

# SocketIO connection handler
@socketio.on('connect')
def handle_connect():
    print("A client connected.")

@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected.")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
