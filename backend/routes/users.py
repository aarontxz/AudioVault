from flask import Blueprint, request, jsonify
import bcrypt
from models import User
from db import db
from routes.utils import token_required

users_routes = Blueprint('users', __name__)

@users_routes.route('/users', methods=['POST'])
@token_required  
def create_user(current_user):
    """
    Creates a new user with the provided username, password, and role.

    Request:
        - JSON body with 'username', 'password', and 'role' fields.
        - Requires a valid JWT token for authentication.

    Response:
        - On success: JSON message indicating the user was created successfully.
        - On failure: JSON error message with status code 400 for missing fields or existing username.
    """
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    password = data.get('password')

    if not username or not password or not role:
        return jsonify({"error": "Username, password and role are required"}), 400
    
    if role != 'member' and role != 'admin':
        return jsonify({"error": "Role must be member or admin"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, role=role, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} created successfully!"}), 201

# Endpoint to retrieve all users
@users_routes.route('/users', methods=['GET'])
@token_required  
def get_users(current_user):  
    """
    Retrieves a list of all users, including their id, username, and role.

    Response:
        - On success: JSON list of users with 'id', 'username', and 'role'.
    """
    users = User.query.filter(User.role != 'master').order_by(User.username, User.id).all()  
    users_data = [
        {"id": user.id, "username": user.username, "role": user.role}
        for user in users
    ] 
    return jsonify({"users": users_data}), 200
    
# Endpoint to delete a user    
@users_routes.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    """
    Deletes a user based on the provided user ID.

    Request:
        - DELETE request to '/users/<id>' where <id> is the user's ID.

    Response:
        - On success: JSON message confirming the user was deleted.
        - On failure: JSON error message if the user is not found (404).
    """
    user_to_delete = User.query.filter_by(id=id).first()
    if user_to_delete.role == 'master':
        jsonify({"error": "cannot delete master"}), 403
    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({"message": "User deleted successfully!"}), 200

@users_routes.route('/users/<id>', methods=['PUT'])
@token_required
def update_user(current_user, id):  
    """
    Updates a user's details (username, role, password).

    Request:
        - PUT request to '/users/<id>' where <id> is the user's ID.
        - JSON body with optional 'username', 'role', and/or 'password' fields to be updated.

    Response:
        - On success: JSON message confirming the user was updated.
        - On failure: 
            - 404 if the user is not found.
            - 400 if the username is already taken by another user.
    """
    data = request.get_json() 
    
    username = data.get('username')
    role = data.get('role')
    password = data.get('password')
    
    user_to_update = User.query.filter_by(id=id).first()
    if username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:  
            return jsonify({"error": "Username already taken by another user"}), 400
    

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404
    
    if username:
        user_to_update.username = username
    if role == 'member' or role == 'admin':
        user_to_update.role = role
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_to_update.password = hashed_password

    db.session.commit()

    return jsonify({"message": f"User {id} updated successfully!"}), 200


@users_routes.route('/users/username', methods=['PUT'])
@token_required
def update_self_username(current_user):
    """
    Updates the username of the authenticated user.

    Request:
        - PUT request to '/users/username'.
        - JSON body with the 'username' field to be updated.

    Response:
        - On success: JSON message confirming the username was updated.
        - On failure:
            - 404 if the user is not found.
            - 400 if the username is already taken by another user.
            - 500 if no new username is provided.
    """
    data = request.get_json() 
    
    username = data.get('username')
    
    user_to_update = User.query.filter_by(id=current_user.id).first()
    if username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:  
            return jsonify({"error": "Username already taken by another user"}), 400

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404
    
    if username:
        user_to_update.username = username
    else:
        return  jsonify({"error": f"Please input a new username"}), 500

    db.session.commit()

    return jsonify({"message": f"Username updated successfully!"}), 200

@users_routes.route('/users/password', methods=['PUT'])
@token_required
def update_self_password(current_user):  
    """
    Updates the password of the authenticated user.

    Request:
        - PUT request to '/users/password'.
        - JSON body with the 'password' field to be updated.

    Response:
        - On success: JSON message confirming the password was updated.
        - On failure:
            - 404 if the user is not found.
            - 500 if no password is provided.
    """
    data = request.get_json() 
    
    password = data.get('password')
    
    user_to_update = User.query.filter_by(id=current_user.id).first()

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404

    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_to_update.password = hashed_password
    else:
        return  jsonify({"error": f"Please input a password"}), 500

    db.session.commit()

    return jsonify({"message": f"User {id} updated successfully!"}), 200