
import sys
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

load_dotenv()

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from ai.email_guard import EmailGuardAI 
app = Flask(__name__)
CORS(app)

AI_GUARDIAN = None
try:
    AI_GUARDIAN = EmailGuardAI(model_path='ai/email_guard_model.joblib')
    app_logger.info("AI Model loaded successfully.")
except FileNotFoundError as e:
    app_logger.error(f"Error loading AI model: {e}")
    app_logger.warning("Please ensure 'ai/email_guard_model.joblib' exists. Run 'python ai/email_guard_model.py' in the project root if it's missing.")
except Exception as e:
    app_logger.error(f"An unexpected error occurred during AI model loading: {e}", exc_info=True)


API_KEY = os.getenv("API_KEY")
if not API_KEY:
    app_logger.warning("WARNING: API_KEY environment variable not set. API access will not be protected. This is INSECURE for production.")

SCAN_HISTORY = []
MAX_HISTORY_SIZE = 100

def authenticate_request():
    if not API_KEY: 
        return True

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        app_logger.warning("Authentication failed: No Authorization header.")
        return False
    try:
        token_type, token = auth_header.split(' ', 1)
        if token_type.lower() == 'bearer' and token == API_KEY:
            return True
        else:
            app_logger.warning(f"Authentication failed: Invalid token type or key. Type: {token_type}, Token: {'*' * len(token) if token else 'None'}")
            return False
    except ValueError:
        app_logger.warning("Authentication failed: Malformed Authorization header.")
        return False

@app.before_request
def before_request_func():
    if request.method == 'OPTIONS':
        return 
    
    if request.path != '/' and not authenticate_request():
        return jsonify({"error": "Unauthorized. Please provide a valid API Key."}), 401

@app.route('/')
def health_check():
    return jsonify({"status": "Email Guardian Backend is running", "model_loaded": AI_GUARDIAN is not None})

@app.route('/scan', methods=['POST'])
def scan_email():
    if AI_GUARDIAN is None:
        return jsonify({"error": "AI model not loaded. Please check server logs and ensure model file exists."}), 500

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request: JSON body is missing or malformed."}), 400

    email_text = data.get('email_text')

    if not email_text or not isinstance(email_text, str) or not email_text.strip():
        return jsonify({"error": "Invalid input. 'email_text' is required and must be a non-empty string."}), 400

    try:
        result = AI_GUARDIAN.classify_email(email_text)
        
        current_time = datetime.now().isoformat()
        SCAN_HISTORY.insert(0, {
            "text_snippet": email_text[:100] + "..." if len(email_text) > 100 else email_text,
            "classification": result["classification"],
            "confidence": result["confidence"],
            "timestamp": current_time
        })
        if len(SCAN_HISTORY) > MAX_HISTORY_SIZE:
            SCAN_HISTORY.pop()

        return jsonify(result), 200
    except Exception as e:
        app_logger.error(f"Error during email scan: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred during scanning: {str(e)}"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({"history": SCAN_HISTORY}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)