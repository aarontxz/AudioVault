from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import bcrypt  # Import bcrypt for password hashing
import jwt  # Import jwt for token handling
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

print(s3_client.list_buckets())

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(30), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}, Role {self.role}>'

# Function to initialize the admin user
def create_admin():
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
            return jsonify({"error": "Your login session has expired please log out and log back in"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


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
@token_required  
def refresh_token():
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

# Endpoint to create a user (POST request)
@app.route('/users', methods=['POST'])
@token_required  
def create_user(current_user):
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
    users = User.query.order_by(User.username, User.id).all()  # Fetch all users from the database
    users_data = [
        {"id": user.id, "username": user.username, "role": user.role}
        for user in users
    ]  # Transform the data into a JSON-serializable format
    return jsonify({"users": users_data}), 200
    
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
@token_required
def update_user(current_user, id):  # Accept current_user from the decorator
    data = request.get_json()  # Get the updated data from the request body
    
    username = data.get('username')
    role = data.get('role')
    password = data.get('password')
    
    # Fetch the user to update by ID
    user_to_update = User.query.filter_by(id=id).first()
    if username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:  
            return jsonify({"error": "Username already taken by another user"}), 400
    

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404
    
    
    # Update the user fields if provided
    if username:
        user_to_update.username = username
    if role:
        user_to_update.role = role
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_to_update.password = hashed_password

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"User {id} updated successfully!"}), 200

@app.route('/users/username', methods=['PUT'])
@token_required
def update_self_username(current_user):  # Accept current_user from the decorator
    data = request.get_json()  # Get the updated data from the request body
    
    username = data.get('username')
    
    # Fetch the user to update by ID
    user_to_update = User.query.filter_by(id=current_user.id).first()
    if username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:  
            return jsonify({"error": "Username already taken by another user"}), 400

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404
    
    
    # Update the user fields if provided
    if username:
        user_to_update.username = username
    else:
        return  jsonify({"error": f"Please input a new username"}), 500
    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"Username updated successfully!"}), 200

@app.route('/users/password', methods=['PUT'])
@token_required
def update_self_password(current_user):  # Accept current_user from the decorator
    data = request.get_json()  # Get the updated data from the request body
    
    password = data.get('password')
    
    # Fetch the user to update by ID
    user_to_update = User.query.filter_by(id=current_user.id).first()

    if not user_to_update:
        return jsonify({"error": "User not found"}), 404

    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_to_update.password = hashed_password
    else:
        return  jsonify({"error": f"Please input a password"}), 500

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"User {id} updated successfully!"}), 200

# AudioFile Model
class AudioFile(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    s3_bucket = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(255), nullable=False)  
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)  
    liked = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<AudioFile {self.file_name}, S3 Path {self.s3_bucket}/{self.s3_key}, Liked: {self.liked}, Shared: {self.share}>"

# Endpoint to create an audio file record
@app.route('/audiofiles', methods=['POST'])
@token_required
def create_audiofile(current_user):
    print(s3_client.list_buckets())
    # Handling file upload
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = file.filename
    
    # Assuming the file is uploaded to S3 (adjust the bucket name)
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


@app.route('/audiofiles', methods=['GET'])
@token_required
def get_audiofiles(current_user):
    audio_files = AudioFile.query.filter_by(user_id=current_user.id).order_by(AudioFile.file_name, AudioFile.id).all()
    audio_files_data = []
    
    for audio_file in audio_files:
        # Retrieve the file content and metadata
        file_data = s3_client.get_object(Bucket=audio_file.s3_bucket, Key=audio_file.s3_key)
        file_content = file_data["Body"].read()  
        
        # Encode the binary content in Base64 for JSON serialization
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # Prepare the response data
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
    # Query the database for the user's audio files
    audio_files = AudioFile.query.filter_by(user_id=current_user.id, liked=True).all()
    audio_files_data = []
    
    for audio_file in audio_files:
        # Retrieve the file content and metadata
        file_data = s3_client.get_object(Bucket=audio_file.s3_bucket, Key=audio_file.s3_key)
        file_content = file_data["Body"].read()
        
        # Encode the binary content in Base64 for JSON serialization
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # Prepare the response data
        audio_files_data.append({
            "id": audio_file.id,
            "file_name": audio_file.file_name,
            "file_content": encoded_content,
            "liked":audio_file.liked
        })
    
    return jsonify({"audiofiles": audio_files_data}), 200

@app.route('/audiofiles/<id>', methods=['DELETE'])
@token_required
def delete_audiofile(current_user, id):
    try:
        # Find the audio file by ID
        audio_file = AudioFile.query.filter_by(id=id, user_id=current_user.id).first()
        
        # If the audio file doesn't exist or doesn't belong to the current user
        if not audio_file:
            return jsonify({"error": "Audio file not found or you do not have permission to delete it"}), 404
        
        # Remove the file from S3
        s3_client.delete_object(Bucket=audio_file.s3_bucket, Key=audio_file.s3_key)
        
        # Delete the record from the database
        db.session.delete(audio_file)
        db.session.commit()
        
        return jsonify({"message": f"Audio file {audio_file.file_name} deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/audiofiles/<id>/like', methods=['PATCH'])
@token_required
def handle_like_file(current_user, id):
    try:
        # Find the audio file by ID and check if it belongs to the current user
        audio_file = AudioFile.query.filter_by(id=id, user_id=current_user.id).first()
        
        # If the audio file doesn't exist or doesn't belong to the current user
        if not audio_file or not current_user.id == audio_file.user_id:
            return jsonify({"error": "Audio file not found"}), 404
        if not current_user.id == audio_file.user_id:
            return jsonify({"error": "You do not have permission to like this file"}), 403
        # Get the liked status from the request
        liked_status = request.json.get('liked')
        
        if liked_status is None:
            return jsonify({"error": "Liked status must be provided"}), 400
        
        # Update the liked status
        audio_file.liked = liked_status
        
        # Commit the changes to the database
        db.session.commit()
        
        # Return the updated liked status
        return jsonify({
            "id": audio_file.id,
            "liked": audio_file.liked
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    create_admin()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
