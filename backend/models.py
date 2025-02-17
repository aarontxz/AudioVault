import uuid
from db import db

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
