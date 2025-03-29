from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def dummy_endpoint():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=True)