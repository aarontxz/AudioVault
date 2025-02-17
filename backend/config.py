import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@db:5432/audiovault'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
