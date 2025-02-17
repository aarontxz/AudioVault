from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from db import db
from routes.audiofiles import audiofiles_routes  # Import the routes for authentication
from routes.users import users_routes
from routes.utils import utils_routes
from routes.utils import create_admin

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

app.register_blueprint(audiofiles_routes)  
app.register_blueprint(users_routes)      
app.register_blueprint(utils_routes)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/audiovault'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

# Create tables if they don't exist and add an admin user 'audiovault' by default
with app.app_context():
    db.init_app(app)  # Initialize the db with the app
    db.create_all()
    create_admin()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
