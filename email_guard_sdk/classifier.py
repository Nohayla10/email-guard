import joblib
import os
import sys
import numpy as np
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import warnings
import importlib.resources as pkg_resources

warnings.filterwarnings("ignore", category=UserWarning, module='nltk')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub(r'\d+', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

class EmailGuardAI:
    _instance = None
    _model = None

    def __new__(cls, model_path=None):
        if cls._instance is None:
            cls._instance = super(EmailGuardAI, cls).__new__(cls)
            cls._instance._load_model(model_path)
        return cls._instance

    def _load_model(self, model_path_override=None):
        docker_model_path = "/app/email_guard_sdk/model/email_guard_model.joblib"

        if model_path_override:
            abs_model_path = os.path.abspath(model_path_override)
            if not os.path.exists(abs_model_path):
                raise FileNotFoundError(f"Model file not found at {abs_model_path}.")
            self._model = joblib.load(abs_model_path)
            print(f"EmailGuardAI model loaded successfully from override path: {abs_model_path}.")
        elif os.path.exists(docker_model_path):
            self._model = joblib.load(docker_model_path)
            print(f"EmailGuardAI model loaded successfully from Docker path: {docker_model_path}.")
        else:
            try:
                with pkg_resources.path('email_guard_sdk.model', 'email_guard_model.joblib') as p:
                    self._model = joblib.load(p)
                print("EmailGuardAI model loaded successfully from SDK package resources.")
            except Exception as e:
                raise FileNotFoundError(f"Failed to load model from SDK package or Docker path: {e}. Ensure 'email_guard_sdk/model/email_guard_model.joblib' exists within the installed package or at {docker_model_path}.")

        self.classes = self._model.classes_

    def classify_email(self, email_text: str):
        if not isinstance(email_text, str) or not email_text.strip():
            return {
                "classification": "invalid_input",
                "confidence": 0.0,
                "explanation": "Input must be a non-empty string.",
                "timestamp": datetime.now().isoformat()
            }

        prediction_proba = self._model.predict_proba([email_text])[0]
        predicted_class_idx = np.argmax(prediction_proba)
        predicted_class = self.classes[predicted_class_idx]
        confidence = prediction_proba[predicted_class_idx]

        explanation = self._generate_explanation(email_text, predicted_class, confidence)

        return {
            "classification": predicted_class,
            "confidence": round(float(confidence), 4),
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_explanation(self, email_text, classification, confidence):
        explanation_map = {
            "phishing": "The email exhibits characteristics commonly found in phishing attempts, such as urgent requests for personal information, suspicious links, or unusual sender addresses. Exercise extreme caution.",
            "spam": "This email is likely unsolicited or promotional, containing common spam indicators like excessive marketing language, irrelevant content, or a high volume of similar messages. Consider blocking the sender.",
            "legit": "This email appears to be legitimate based on its content and structure. However, always double-check sender details and links, especially if it's unexpected or asks for sensitive information."
        }

        base_explanation = explanation_map.get(classification, "Unable to provide a detailed explanation for this classification.")

        email_text_lower = email_text.lower()
        if "link" in email_text_lower or "http" in email_text_lower or "https" in email_text_lower:
            base_explanation += " The presence of links is noted; always hover over links before clicking to verify their destination."
        
        common_phishing_keywords = ["verify", "account", "urgent", "security", "password", "bank", "update information", "suspended", "action required", "invoice", "payment", "reset password"]
        if any(keyword in email_text_lower for keyword in common_phishing_keywords):
            base_explanation += " Keywords related to account verification or security were detected, which are common in phishing attempts."
        
        if classification == "spam" and any(keyword in email_text_lower for keyword in ["free", "won", "prize", "congratulations", "guarantee", "discount", "offer"]):
            base_explanation += " Common spam terms like 'free', 'won', or 'prize' were identified."
        
        if confidence < 0.7:
            base_explanation += f" (Confidence: {confidence*100:.2f}% is moderate, further manual review is recommended.)"
        elif confidence < 0.5:
            base_explanation += f" (Confidence: {confidence*100:.2f}% is low, the classification might be uncertain.)"

        return base_explanation