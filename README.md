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
MASTER_PASSWORD=<a user with a special role master with username master will be created when first initializing the app, set the password for this special user here>
```

### 5. build and run the docker image
```bash
docker-compose up --build
```


## EC2 Setup

Create an EC2 instance with permissions to access your s3 bucket

Connect into your EC2 and Follow these steps to set up and run the application on your EC2 instance:

### 1. Update and Install Docker
Run the following commands to install and configure Docker:
```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
docker --version
```

### 2. Log in to Docker and Pull Images
```
docker login
docker pull aarontxz/audiovault-frontend:latest
docker pull aarontxz/audiovault-backend:latest
docker pull aarontxz/postgres:13
```
### 3. Set the required environment variables
```
export REACT_APP_BACKEND_URL=<your public ip:5000>
export MASTER_PASSWORD=<set the password of the special user master>
```

### 4, Run the containers
```
docker run -d --network backend-network --name audiovault-frontend -p 3000:3000 \
    -e REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL aarontxz/audiovault-frontend

docker run -d --network backend-network --name audiovault-backend -p 5000:5000 \
    -e REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL \
    -e MASTER_PASSWORD=$MASTER_PASSWORD aarontxz/audiovault-backend

docker run -d --network backend-network --name audiovault-db -p 5432:5432   -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=audiovault   aarontxz/postgres:13
```

## how to redeploy on ec2

### 1. in your local environment tag and push changes
```
docker compose -up
docker tag audiovault-frontend aarontxz/audiovault-frontend:latest
docker tag audiovault-backend aarontxz/audiovault-backend:latest
docker push aarontxz/audiovault-frontend:latest                   
docker push aarontxz/audiovault-backend:latest                 
```

### 2. connect to your EC2 and run the following commands

```
docker stop audiovault-frontend
docker stop audiovault-backend
docker rm audiovault-frontend
docker rm audiovault-backend
docker run -d --network backend-network --name audiovault-frontend -p 3000:3000 \
    -e REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL aarontxz/audiovault-frontend
docker run -d --network backend-network --name audiovault-backend -p 5000:5000 \
    -e REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL \
    -e MASTER_PASSWORD=$MASTER_PASSWORD aarontxz/audiovault-backend
```


## Accessing the Database Inside the Container

To access the database running inside the Docker container, follow these steps:

### 1. Connect to Your EC2 Instance

### 2. Find the Database Container ID
Run the following command to list all running containers and identify the database container:
```bash
docker ps
```

### 3. use this exec command to get inside the container
```
docker exec -it <db-container-id> bash
```

### 4. once inside the container you can use the PostgreSQL CLI to interact with the database:
```
psql -U user -d audiovault
```
