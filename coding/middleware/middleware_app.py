from flask import Flask, jsonify, request
from dotenv import load_dotenv
from middleware_data_classes import create_database
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import secrets

# loads properties.env
load_dotenv()

# create database
create_database()

app = Flask(__name__)

@app.route('/')
def dummy_endpoint():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=True)
