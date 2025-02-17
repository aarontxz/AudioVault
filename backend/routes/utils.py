import os 
import db
from models import User
from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import bcrypt  
import jwt
import datetime

utils_routes = Blueprint('utils', __name__)

def create_admin():
    """
    Checks if an admin user exists. If not, creates a new admin with the username 'audiovault' 
    and a hashed password. The admin's role is set to 'admin'.
    This function is intended to be called when initializing the database for the first time.
    """
    try:
        # Check if the master already exists
        admin = User.query.filter_by(username='master').first()
        master_password = os.getenv('MASTER_PASSWORD', '')
        if not admin:
            # Create a new master if none exists
            hashed_password = bcrypt.hashpw(master_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username='master',
                password=hashed_password,
                role='master'
            )
            db.session.add(admin)
            db.session.commit()
    except:
        db.session.rollback()
        
def token_required(f):
    """
    Decorator to ensure a valid JWT token is present in the request header.

    The token is decoded using the app's secret key, and the user is authenticated. If the token is missing, 
    expired, or invalid, a 401 error is returned. Otherwise, the current user is passed to the route handler.

    Args:
        f (function): The route handler function to be wrapped.

    Returns:
        function: The decorated route handler with added token validation logic.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200 

        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            token = token.split(" ")[1] 
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({"error": "Your login session has expired please log out and log back in"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@utils_routes.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user by validating the provided username and password.

    If successful, issues an access token (valid for 2 hours) and a refresh token (valid for 7 days).

    Request:
        - JSON body with 'username' and 'password' fields.

    Response:
        - On success: JSON containing 'access_token', 'refresh_token', 'user_id', and 'user_role'.
        - On failure: JSON error message with status code 401 for invalid username, 402 for invalid password.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username"}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Invalid password"}), 402

    # Generate JWT tokens
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=120)  # Token expires in 120 mins
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    refresh_token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now() + datetime.timedelta(days=7)  # Refresh token expires in 7 days
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"access_token": token, "refresh_token": refresh_token, "user_id": user.id, "user_role": user.role}), 200

@utils_routes.route('/refresh', methods=['POST'])
@token_required  
def refresh_token():
    """
    Refreshes the access token using a valid refresh token.

    Request:
        - Authorization header containing the refresh token in the format 'Bearer <token>'.

    Response:
        - On success: JSON with a new 'access_token'.
        - On failure: JSON error message with status code 401 for missing or invalid refresh token.
    """
    refresh_token = request.headers.get('Authorization')
    if not refresh_token:
        return jsonify({"error": "Refresh token is missing"}), 401

    try:
        refresh_token = refresh_token.split(" ")[1]
        data = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        new_token = jwt.encode({
            'user_id': data['user_id'],
            'exp': datetime.datetime.now() + datetime.timedelta(minutes=15)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"access_token": new_token}), 200
    except Exception as e:
        return jsonify({"error": "Invalid refresh token"}), 401
