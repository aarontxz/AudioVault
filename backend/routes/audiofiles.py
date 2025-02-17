from flask import Blueprint, jsonify, request
import uuid
import base64
from db import db
from routes.utils import token_required
from models import AudioFile
from s3_client import s3_client

audiofiles_routes = Blueprint('audiofiles', __name__)

@audiofiles_routes.route('/audiofiles', methods=['POST'])
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
@audiofiles_routes.route('/audiofiles', methods=['GET'])
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

@audiofiles_routes.route('/audiofiles/favourites', methods=['GET'])
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
@audiofiles_routes.route('/audiofiles/<id>', methods=['DELETE'])
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
    

@audiofiles_routes.route('/audiofiles/<id>/like', methods=['PATCH'])
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