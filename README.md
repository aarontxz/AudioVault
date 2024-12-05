# AudioVault
Audio File Hosting Web Application

AudioVault is a platform for users to upload/playback audio files and Admin to manage these users. The application includes authentication using JWT tokens, role-based user access, and integrates with S3 for audio file storage.

## Video walk through for AudioVault
https://youtu.be/4bY9Knj95gw

## Features

- **User Authentication**: Sign in using a username and password. JWT tokens are issued for access and refresh.
- **User Management**: Create new users, update user details, and delete users.
- **Audio File Management**: Upload audio files, like/dislike files, and delete files from both the database and S3 storage.
- **Role-Based Access Control**: Different user roles with varying access levels.
- **Security**: All endpoints require authentication using Bearer JWT tokens.
- **Credential Storage**: User passwords are securely hashed using bcrypt before being stored in the database, ensuring safe handling of sensitive information.

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

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/aarontxz/AudioVault.git
cd AudioVault
```

### 2. Prepare an S3 Bucket

Create an S3 bucket named `audiovault-s3`.  
This bucket will serve as the storage for audio files and related resources. Ensure that the bucket name matches exactly as `audiovault-s3`.

#### 3. Create an IAM User with Permissions  

Create an IAM user and attach the following policy to grant access to the `audiovault-s3` bucket. 

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::audiovault-s3",
                "arn:aws:s3:::audiovault-s3/*"
            ],
            "Effect": "Allow"
        }
    ]
}
```

After creating the IAM user, generate an Access Key ID and Secret Access Key for the user. These credentials will be required to connect your application to the S3 bucket.


### 4. Create a `.env` File with These Variables  

Set up a `.env` file in your project directory and include the following environment variables:  

```plaintext
AWS_ACCESS_KEY_ID=<replace this with the Access Key ID>
AWS_SECRET_ACCESS_KEY=<replace this with the Secret Access Key>
AWS_DEFAULT_REGION=<replace this with the appropriate region for the S3 bucket>
FLASK_APP=app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_ENV=development 
FLASK_DEBUG=1 
FLASK_SECRET_KEY=AudioVaultKey
REACT_APP_BACKEND_URL=http://localhost:5000 # Change this if not deploying locally
CHOKIDAR_USEPOLLING=true
```

### 5. build and run the docker image
```bash
docker-compose up --build
```
