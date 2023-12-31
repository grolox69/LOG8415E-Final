from flask import Flask, request, jsonify
import requests
import re 

app = Flask(__name__)

# Configuration
PROXY_URL = 'http://<proxy_ip>:<proxy_port>'

def validate_request(req):
    """ Basic request validation. Expand as needed. """
    # Example: Reject if request body contains suspicious patterns
    if re.search(r'[^\w\s]', req.json.get('data', '')):
        return False
    return True

@app.route('/handle_request', methods=['POST'])
def handle_request():
    if not validate_request(request):
        return jsonify({"error": "Invalid request"}), 400

    # Forward the validated request to the proxy
    response = requests.post(PROXY_URL, json=request.json)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)