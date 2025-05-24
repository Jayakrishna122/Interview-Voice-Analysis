from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask Server is Running!"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    file_path = data.get('file_path', '')
    return jsonify({
        "message": "Received file path!",
        "file_path": file_path
    })

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
