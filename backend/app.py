from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import bcrypt  # Import bcrypt for password hashing
import jwt  # Import jwt for token handling
import datetime
import os
from enum import Enum

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/audiovault'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

# Initialize SQLAlchemy
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    password = db.Column(db.String(120), nullable=False)
    files = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<User {self.username}, Role {self.role}>'

# Function to initialize the admin user
def create_admin():
    try:
        # Check if the admin already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create a new admin if none exists
            hashed_password = bcrypt.hashpw('audiovault'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username='audiovault',
                password=hashed_password,
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
    except:
        db.session.rollback()

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    create_admin() 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow OPTIONS requests (preflight) to pass through without requiring a token
        if request.method == 'OPTIONS':
            return '', 200  # Return 200 OK for OPTIONS requests to allow CORS preflight

        # Handle the regular requests (POST, GET, etc.)
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            token = token.split(" ")[1]  # Remove "Bearer" prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


# Endpoint to test the connection
@app.route('/home')
def home():
    return jsonify(message="Hello from Flask!")

# Endpoint to create a user (POST request)
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    password = data.get('password')

    if not username or not password or not role:
        return jsonify({"error": "Username, password and role are required"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, role=role, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} created successfully!"}), 201

@app.route('/users', methods=['GET'])
@token_required  
def get_users(current_user):  # Accept current_user passed from the decorator
    users = User.query.all()  # Fetch all users from the database
    users_data = [
        {"id": user.id, "username": user.username, "role": user.role, "files": user.files}
        for user in users
    ]  # Transform the data into a JSON-serializable format
    return jsonify({"users": users_data}), 200

# Endpoint to authenticate a user and issue a JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    print(username)

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username"}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Invalid password"}), 402

    # Generate JWT tokens
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=15)  # Token expires in 15 mins
    }, app.config['SECRET_KEY'], algorithm="HS256")

    refresh_token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now() + datetime.timedelta(days=7)  # Refresh token expires in 7 days
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"access_token": token, "refresh_token": refresh_token, "user_id": user.id, "user_role": user.role}), 200

# Endpoint to refresh the access token
@app.route('/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.headers.get('Authorization')
    if not refresh_token:
        return jsonify({"error": "Refresh token is missing"}), 401

    try:
        refresh_token = refresh_token.split(" ")[1]
        data = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        new_token = jwt.encode({
            'user_id': data['user_id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"access_token": new_token}), 200
    except Exception as e:
        return jsonify({"error": "Invalid refresh token"}), 401
    
@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    user_to_delete = User.query.filter_by(id=id).first()
    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404

    # Delete the user
    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({"message": "User deleted successfully!"}), 200

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):  # Accept current_user from the decorator
    data = request.get_json()  # Get the updated data from the request body
    
    username = data.get('username')
    role = data.get('role')
    password = data.get('password')
    
    # Fetch the user to update by ID
    user_to_update = User.query.filter_by(id=id).first()

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404
    
    
    # Update the user fields if provided
    if username:
        user_to_update.username = username
    if role:
        user_to_update.role = role
    if password:
        hashed_password = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_to_update.password = hashed_password

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"User {id} updated successfully!"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
