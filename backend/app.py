from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/audiovault'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    files = db.Column(db.JSON, nullable=True) 

    def __repr__(self):
        return f'<User {self.username}>'
    
# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Endpoint to test the connection
@app.route('/home')
def home():
    return jsonify(message="Hello from Flask!")

# Endpoint to create a user (POST request)
@app.route('/users', methods=['POST'])
def create_user():
    # Get JSON data from the request body
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    files = data.get('files', [])  # Default to an empty list if 'files' is not provided

    # Check if the required data is provided
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if the username or password already exists
    existing_user = User.query.filter((User.username == username)).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    # Create a new User instance
    new_user = User(username=username, password=password, files=files)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} created successfully!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
