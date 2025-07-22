import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

try:
    from email_guard_sdk.classifier import EmailGuardAI
except ImportError as e:
    print(f"ERROR: Could not import EmailGuardAI from SDK. Ensure 'email_guard_sdk' is correctly installed. Error: {e}", file=sys.stderr)
    email_guardian = None
app = Flask(__name__)
CORS(app)

if 'email_guardian' not in locals() or email_guardian is None:
    try:
        email_guardian = EmailGuardAI()
        print("EmailGuardAI model loaded successfully for backend.", flush=True)
    except Exception as e:
        print(f"ERROR: Failed to load EmailGuardAI model at backend startup: {e}", file=sys.stderr, flush=True)
        email_guardian = None
SCAN_HISTORY = []
API_KEY = os.getenv("API_KEY")
print(f"API_KEY status: {'Set' if API_KEY else 'Not Set (auth skipped)'}", flush=True)

def authenticate_api_key():
    if API_KEY:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False, jsonify({"error": "Unauthorized: Bearer token missing"}), 401
        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return False, jsonify({"error": "Unauthorized: Invalid API key"}), 401
    return True, None, None

@app.route('/')
def health_check():
    if email_guardian is None:
        return jsonify({"status": "EmailGuard Backend: Model Not Loaded", "model_operational": False}), 503
    return jsonify({"status": "EmailGuard Backend is running!", "model_operational": True}), 200

@app.route('/scan', methods=['POST'])
def scan_email():
    auth_success, auth_response, auth_status = authenticate_api_key()
    if not auth_success:
        return auth_response, auth_status
    data = request.get_json()
    email_text = data.get('email_text')
    if not email_text or not isinstance(email_text, str):
        return jsonify({"error": "Invalid input: 'email_text' must be a non-empty string."}), 400
    if email_guardian is None:
        return jsonify({"error": "AI model not loaded. Backend is not operational for classification."}), 500
    try:
        result = email_guardian.classify_email(email_text)
        history_entry = {
            "email_preview": (email_text[:100] + "...") if len(email_text) > 100 else email_text,
            "classification": result['classification'],
            "confidence": result['confidence'],
            "timestamp": result['timestamp']
        }
        SCAN_HISTORY.insert(0, history_entry)
        if len(SCAN_HISTORY) > 50:
            SCAN_HISTORY.pop()
        return jsonify(result), 200
    except Exception as e:
        print(f"Error during email classification: {e}", file=sys.stderr, flush=True)
        return jsonify({"error": f"An error occurred during classification: {e}"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    auth_success, auth_response, auth_status = authenticate_api_key()
    if not auth_success:
        return auth_response, auth_status
    return jsonify({"history": SCAN_HISTORY}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask app locally on http://0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=True)