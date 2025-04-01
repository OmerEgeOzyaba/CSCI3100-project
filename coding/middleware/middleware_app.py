from flask import Flask, jsonify
from dotenv import load_dotenv
from middleware_data_classes import create_database

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