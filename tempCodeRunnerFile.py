from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt, checkpw


app = Flask(__name__)

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

# Create the database tables
with app.app_context():
    db.create_all()

# Register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
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

if __name__ == '__main__':
    app.run(debug=True)
