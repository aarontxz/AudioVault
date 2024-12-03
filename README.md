# AudioVault
Audio File Hosting Web Application

AudioVault is a secure platform for managing audio files, users, and authentication. It allows users to upload, like, and delete audio files while maintaining an organized, user-centric management system. The application includes authentication using JWT tokens, role-based user management, and integrates with S3 for audio file storage.

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

### 2. build and run the docker image
```bash
docker compose up
```
