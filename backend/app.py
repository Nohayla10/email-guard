import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import warnings
import datetime
from datetime import timezone

try:
    from email_guard_sdk.classifier import EmailGuardAI
except ImportError as e:
    print(f"Error importing EmailGuardAI from SDK: {e}. Ensure 'email_guard_sdk' is installed.", file=sys.stderr)
    sys.exit(1)

warnings.filterwarnings("ignore", category=UserWarning, module='nltk')

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    email_guard_ai = EmailGuardAI()
except FileNotFoundError as e:
    print(f"Error loading AI model: {e}. Please ensure 'email_guard_sdk' is correctly installed and model file exists within it.", file=sys.stderr)
    email_guard_ai = None

SCAN_HISTORY = []

@app.route('/')
def home():
    return jsonify({"message": "EmailGuard API is running!"})

@app.route('/scan', methods=['POST'])
def scan_email():
    API_KEY = os.getenv("API_KEY") 
    if API_KEY:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized: Bearer token missing"}), 401
        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401

    data = request.get_json()
    email_text = data.get('email_text')

    if not email_text or not isinstance(email_text, str) or not email_text.strip():
        return jsonify({"error": "Invalid input. 'email_text' is required and must be a non-empty string."}), 400

    if not email_guard_ai:
        return jsonify({"error": "AI model not loaded. Cannot process request."}), 500

    result = email_guard_ai.classify_email(email_text)

    SCAN_HISTORY.append({
        "input": email_text,
        "text_snippet": email_text[:100] + ('...' if len(email_text) > 100 else ''),
        "classification": result.get("classification"),
        "confidence": result.get("confidence"),
        "timestamp": datetime.datetime.now(timezone.utc).isoformat()
    })
    if len(SCAN_HISTORY) > 100:
        SCAN_HISTORY.pop(0)

    return jsonify(result)

@app.route('/history', methods=['GET'])
def get_history():
    API_KEY= os.getenv("API_KEY") 
    if API_KEY:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized: Bearer token missing"}), 401
        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401
    
    return jsonify({"history": SCAN_HISTORY})