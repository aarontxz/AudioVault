# AudioVault
Audio File Hosting Web Application

AudioVault is a secure platform for users to upload/playback Audiofiles and Admin to manage these users. The application includes authentication using JWT tokens, role-based user access, and integrates with S3 for audio file storage.

## Video walk through for AudioVault
https://youtu.be/4bY9Knj95gw

## Features

- **User Authentication**: Sign in using a username and password. JWT tokens are issued for access and refresh.
- **User Management**: Create new users, update user details, and delete users.
- **Audio File Management**: Upload audio files, like/dislike files, and delete files from both the database and S3 storage.
- **Role-Based Access Control**: Different user roles with varying access levels.
- **Security**: All endpoints require authentication using Bearer JWT tokens.

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL (PSQL)
- **Authentication**: JWT (JSON Web Tokens)
- **Storage**: Amazon S3 for audio file storage
- **API Documentation**: OpenAPI 3.0

## Requirements

- Python 3.x
- Flask
- psycopg2 (PostgreSQL adapter for Python)
- SQLAlchemy (for ORM support)
- AWS SDK (boto3)
- OpenAPI/Swagger documentation tools

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/aarontxz/AudioVault.git
cd AudioVault
```

### 2. create a .env file with these variables
AWS_ACCESS_KEY_ID=<replace this with the AWS_ACCESS_KEY_ID to access to s3>
AWS_SECRET_ACCESS_KEY=<replace this with the AWS_SECRET_ACCESS_KEY to access to s3>
AWS_DEFAULT_REGION=<replace this with the appropriate region for the s3 bucket>
FLASK_APP=app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_ENV=development 
FLASK_DEBUG=1 
FLASK_SECRET_KEY=AudioVaultKey
REACT_APP_BACKEND_URL=http://backend:5000
CHOKIDAR_USEPOLLING=true


### 3. build and run the docker image
```bash
docker-compose up --build
```
