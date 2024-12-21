import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
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

# Configure MongoDB
app.config['MONGO_URI'] = 'postgresql://dbdbase_user:w82vkLMjw6Q4UoApnlzIjtCCCwIku0c9@dpg-ctjebsd2ng1s73bj0e70-a/dbdbase'  # MongoDB URI
mongo = PyMongo(app)

# User collection (MongoDB does not require predefined schema, but we can define a structure)
users_collection = mongo.db.users

# Messages collection
messages_collection = mongo.db.messages

# Register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    users_collection.insert_one({'username': username, 'password': hashed_password})

    return jsonify({"message": "User registered successfully"}), 201

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})
    if not user or not checkpw(password.encode('utf-8'), user['password']):
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

    sender = users_collection.find_one({'username': sender_username})
    receiver = users_collection.find_one({'username': receiver_username})

    if not sender or not receiver:
        return jsonify({"message": "Sender or receiver not found"}), 404

    try:
        new_message = {
            'sender_id': sender['_id'],
            'receiver_id': receiver['_id'],
            'content': content,
            'timestamp': datetime.utcnow()
        }
        messages_collection.insert_one(new_message)

        message_data = {
            'sender': sender['username'],
            'receiver': receiver['username'],
            'content': content,
            'timestamp': new_message['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        }
        socketio.emit('new_message', message_data)
        print("Message emitted to frontend: ", message_data)  # Log message emission

        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        return jsonify({"message": f"Error sending message: {str(e)}"}), 500

# Get Messages Endpoint
@app.route('/messages/<username>', methods=['GET'])
def get_messages(username):
    user = users_collection.find_one({'username': username})

    if not user:
        return jsonify({"message": "User not found"}), 404

    received_messages = messages_collection.find({'receiver_id': user['_id']})
    sent_messages = messages_collection.find({'sender_id': user['_id']})

    received = [{"sender": str(msg['sender_id']), "content": msg['content'], "timestamp": msg['timestamp']} for msg in received_messages]
    sent = [{"receiver": str(msg['receiver_id']), "content": msg['content'], "timestamp": msg['timestamp']} for msg in sent_messages]

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
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
