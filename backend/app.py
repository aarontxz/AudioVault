from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import bcrypt  
import jwt
import datetime
import os
import boto3
import base64

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/audiovault'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

db = SQLAlchemy(app)
s3_client = boto3.client('s3', region_name='ap-southeast-1')

class User(db.Model):
    """
    Represents a user in the database.

    Attributes:
        id (str): Unique identifier for the user, generated as a UUID.
        username (str): The user's username, must be unique.
        role (str): The user's role either admin or member, defaults to member
        password (str): The user's hashed password.

    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(30), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}, Role {self.role}>'

def create_admin():
    """
    Checks if an admin user exists. If not, creates a new admin with the username 'audiovault' 
    and a hashed password. The admin's role is set to 'admin'.

    This function is intended to be called when initializing the database for the first time.
    """
    try:
        # Check if the admin already exists
        admin = User.query.filter_by(username='audiovault').first()
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
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({"error": "Your login session has expired please log out and log back in"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/login', methods=['POST'])
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
    print(username)

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username"}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Invalid password"}), 402

    # Generate JWT tokens
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=120)  # Token expires in 120 mins
    }, app.config['SECRET_KEY'], algorithm="HS256")

    refresh_token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now() + datetime.timedelta(days=7)  # Refresh token expires in 7 days
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"access_token": token, "refresh_token": refresh_token, "user_id": user.id, "user_role": user.role}), 200

# This function istn being used currently 
@app.route('/refresh', methods=['POST'])
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
        data = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        new_token = jwt.encode({
            'user_id': data['user_id'],
            'exp': datetime.datetime.now() + datetime.timedelta(minutes=15)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"access_token": new_token}), 200
    except Exception as e:
        return jsonify({"error": "Invalid refresh token"}), 401


@app.route('/users', methods=['POST'])
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

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, role=role, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} created successfully!"}), 201

# Endpoint to retrieve all users
@app.route('/users', methods=['GET'])
@token_required  
def get_users(current_user):  
    """
    Retrieves a list of all users, including their id, username, and role.

    Response:
        - On success: JSON list of users with 'id', 'username', and 'role'.
    """
    users = User.query.order_by(User.username, User.id).all()  
    users_data = [
        {"id": user.id, "username": user.username, "role": user.role}
        for user in users
    ] 
    return jsonify({"users": users_data}), 200
    
# Endpoint to delete a user    
@app.route('/users/<id>', methods=['DELETE'])
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
    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify({"message": "User deleted successfully!"}), 200

@app.route('/users/<id>', methods=['PUT'])
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
    if role:
        user_to_update.role = role
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_to_update.password = hashed_password

    db.session.commit()

    return jsonify({"message": f"User {id} updated successfully!"}), 200


@app.route('/users/username', methods=['PUT'])
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

@app.route('/users/password', methods=['PUT'])
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

class AudioFile(db.Model):
    """
    Represents an audio file uploaded to S3 by a user.

    Attributes:
        id (str): Unique identifier for the audio file (primary key).
        file_name (str): Name of the audio file.
        s3_bucket (str): S3 bucket where the audio file is stored.
        s3_key (str): Key for the audio file in the S3 bucket. (currently s3_key is simply the id)
        user_id (str): ID of the user who uploaded the audio file (foreign key).
        liked (bool): Indicates whether the audio file is liked by the user (default: False).
    """
    id = db.Column(db.String(36), primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    s3_bucket = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(255), nullable=False)  
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)  
    liked = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<AudioFile {self.file_name}, S3 Path {self.s3_bucket}/{self.s3_key}, Liked: {self.liked}, Shared: {self.share}>"

@app.route('/audiofiles', methods=['POST'])
@token_required
def create_audiofile(current_user):
    """
    Creates a new audio file, uploads it to an S3 bucket, and also stores the file information in the database.

    Request:
        - POST request to '/audiofiles' with the file uploaded as part of the form-data.
        
    Response:
        - On success: JSON message confirming the file was uploaded successfully.
        - On failure:
            - 400 if no file is provided or no file is selected.
            - 500 if there was an error during the file upload or database operation.
    """
    print(s3_client.list_buckets())
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = file.filename
    s3_bucket = 'audiovault-s3'
    id = str(uuid.uuid4())
    s3_key = id
    
    try:
        audio_file = AudioFile(
            id = id,
            file_name=filename,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            user_id=current_user.id
        )
        s3_client.upload_fileobj(file, s3_bucket, s3_key)
        db.session.add(audio_file)
        db.session.commit()
        
        return jsonify({"message": f"Audio file {filename} uploaded successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to getch all audiofiles and their information from s3
@app.route('/audiofiles', methods=['GET'])
@token_required
def get_audiofiles(current_user):
    """
    Retrieves all audio files uploaded by the authenticated user and their metadata, 
    including the file content encoded in Base64.
        
    Response:
        - On success: JSON containing all the user's audio files, with each file's metadata 
          and content (encoded in Base64).
        - On failure: 404 if no audio files are found for the user.
    """
    audio_files = AudioFile.query.filter_by(user_id=current_user.id).order_by(AudioFile.file_name, AudioFile.id).all()
    audio_files_data = []
    
    for audio_file in audio_files:
        file_data = s3_client.get_object(Bucket=audio_file.s3_bucket, Key=audio_file.s3_key)
        file_content = file_data["Body"].read()  
        
        # Encode the binary content in Base64 for JSON serialization
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        audio_files_data.append({
            "id": audio_file.id,
            "file_name": audio_file.file_name,
            "file_content": encoded_content,
            "liked":audio_file.liked
        })
    
    return jsonify({"audiofiles": audio_files_data}), 200

@app.route('/audiofiles/favourites', methods=['GET'])
@token_required
def get_favourite_audiofiles(current_user):
    """
    Retrieves all audio files that the authenticated user has marked as liked (favourites),
    along with their metadata and content (encoded in Base64).
        
    Response:
        - On success: JSON containing all the user's favourite audio files, 
          with each file's metadata and content (encoded in Base64).
        - On failure: 404 if no favourite audio files are found for the user.
    """
    audio_files = AudioFile.query.filter_by(user_id=current_user.id, liked=True).all()
    audio_files_data = []
    
    for audio_file in audio_files:
        file_data = s3_client.get_object(Bucket=audio_file.s3_bucket, Key=audio_file.s3_key)
        file_content = file_data["Body"].read()
        
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        audio_files_data.append({
            "id": audio_file.id,
            "file_name": audio_file.file_name,
            "file_content": encoded_content,
            "liked":audio_file.liked
        })
    
    return jsonify({"audiofiles": audio_files_data}), 200

# Endpoint to delete an audiofile
@app.route('/audiofiles/<id>', methods=['DELETE'])
@token_required
def delete_audiofile(current_user, id):
    """
    Deletes an audio file both from the S3 bucket and the database.

    Request:
        - DELETE request to '/audiofiles/<id>', where <id> is the audio file ID.
        
    Response:
        - On success: JSON message confirming the audio file was deleted.
        - On failure:
            - 404 if the audio file is not found or the user does not have permission.
            - 500 if there was an error during the deletion process.
    """
    try:
        audio_file = AudioFile.query.filter_by(id=id, user_id=current_user.id).first()
        
        if not audio_file:
            return jsonify({"error": "Audio file not found or you do not have permission to delete it"}), 404
        
        s3_client.delete_object(Bucket=audio_file.s3_bucket, Key=audio_file.s3_key)
        
        db.session.delete(audio_file)
        db.session.commit()
        
        return jsonify({"message": f"Audio file {audio_file.file_name} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/audiofiles/<id>/like', methods=['PATCH'])
@token_required
def handle_like_file(current_user, id):
    """
    Allows the authenticated user to like or unlike their own audio file.

    Request:
        - PATCH request to '/audiofiles/<id>/like', where <id> is the audio file ID.
        - JSON body with the 'liked' status (True/False) to indicate whether the file is liked.
        
    Response:
        - On success: JSON with the audio file ID and updated liked status.
        - On failure:
            - 404 if the audio file is not found.
            - 403 if the user does not have permission to like the file.
            - 400 if the liked status is not provided.
    """
    try:
        audio_file = AudioFile.query.filter_by(id=id, user_id=current_user.id).first()
        
        if not audio_file or not current_user.id == audio_file.user_id:
            return jsonify({"error": "Audio file not found"}), 404
        if not current_user.id == audio_file.user_id:
            return jsonify({"error": "You do not have permission to like this file"}), 403

        liked_status = request.json.get('liked')
        
        if liked_status is None:
            return jsonify({"error": "Liked status must be provided"}), 400

        audio_file.liked = liked_status

        db.session.commit()

        return jsonify({
            "id": audio_file.id,
            "liked": audio_file.liked
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Create tables if they don't exist and add an admin user 'audiovault' by default
with app.app_context():
    db.create_all()
    create_admin()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
