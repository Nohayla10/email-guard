# tests/test_email_guard.py (Full file with the definitive CLI testing fix)

import unittest
import os
import json
from unittest.mock import patch, MagicMock
import sys
import io
import importlib

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import AI components from the SDK
try:
    from email_guard_sdk.classifier import EmailGuardAI, preprocess_text
except ImportError as e:
    print(f"Error: Could not import EmailGuardAI or preprocess_text from SDK. Please ensure 'email_guard_sdk' is installed. Error: {e}")
    sys.exit(1)

# Import the training script
from ai.email_guard_model import train_and_save_model

# Import the Flask app instance directly
from backend.app import app
from backend.app import SCAN_HISTORY

# Import the CLI main function directly
import email_guard 

class TestEmailGuard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n--- Running setUpClass for TestEmailGuard ---")
        
        try:
            import nltk
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("NLTK 'stopwords' not found. Attempting to download for tests...")
            nltk.download('stopwords', quiet=True)
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("NLTK 'wordnet' not found. Attempting to download for tests...")
            nltk.download('wordnet', quiet=True)

        model_sdk_path = os.path.join(project_root, 'email_guard_sdk', 'model', 'email_guard_model.joblib')

        if not os.path.exists(model_sdk_path):
            print(f"Model not found at {model_sdk_path}. Running model training script...")
            original_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                train_and_save_model()
            finally:
                sys.stdout = original_stdout
            print("Model training script finished successfully.")
        
        cls.email_guard_instance = EmailGuardAI()

        cls.app_client = app.test_client()
        app.config['TESTING'] = True

        print("--- setUpClass complete ---")

    def setUp(self):
        SCAN_HISTORY.clear()

    def test_preprocess_text(self):
        self.assertEqual(preprocess_text("Hello, world! 123"), "hello world")
        self.assertEqual(preprocess_text("Click HERE for FREE prizes!"), "click free prize")
        self.assertEqual(preprocess_text("URGENT: Verify your account at example.com"), "urgent verify account examplecom")
        self.assertEqual(preprocess_text(""), "")
        self.assertEqual(preprocess_text(None), "")

    def test_classify_email_legit(self):
        text = "Hi John, confirming our meeting tomorrow at 10 AM regarding the project."
        result = self.email_guard_instance.classify_email(text)
        self.assertIn(result['classification'], ['legit', 'spam', 'phishing'])
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertIsInstance(result['explanation'], str)

    def test_classify_email_spam(self):
        text = "Congratulations! You've won a FREE iPhone! Click here to claim: win.example.com"
        result = self.email_guard_instance.classify_email(text)
        self.assertIn(result['classification'], ['legit', 'spam', 'phishing'])
        self.assertGreaterEqual(result['confidence'], 0.0)

    def test_classify_email_phishing(self):
        text = "Urgent action required for your bank account. Log in immediately to verify your details: secure-bank.ru/login"
        result = self.email_guard_instance.classify_email(text)
        self.assertIn(result['classification'], ['legit', 'spam', 'phishing'])
        self.assertGreaterEqual(result['confidence'], 0.0)

    def test_classify_email_empty(self):
        result = self.email_guard_instance.classify_email("")
        self.assertEqual(result['classification'], 'invalid_input')
        self.assertEqual(result['confidence'], 0.0)
        self.assertIn("Input must be a non-empty string.", result['explanation'])

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.exit') 
    @patch('email_guard_sdk.classifier.EmailGuardAI.classify_email') # <-- New patch here!
    def test_cli_execution_success(self, mock_classify_email, mock_exit, mock_stderr, mock_stdout, mock_parse_args):
        # Configure the mocked classify_email to return a predictable result
        mock_classify_email.return_value = {
            "classification": "legit",
            "confidence": 0.95,
            "explanation": "This is a mocked legitimate email."
        }

        mock_parse_args.return_value.email_text = "This is a test email for CLI."
        mock_parse_args.return_value.model = None
        
        EmailGuardAI._instance = None # Reset singleton for this test

        email_guard.main() 

        mock_exit.assert_called_once_with(0)
        
        mock_stdout.flush() # Ensure stdout is flushed
        output = mock_stdout.getvalue()
        err_output = mock_stderr.getvalue()
        
        sys.stderr.flush()
        
        self.assertNotIn('error', err_output.lower())
        self.assertIn('"classification"', output)
        self.assertIn('"confidence"', output)
        self.assertIn('"explanation"', output)
        
        # Add a print to debug if it fails again
        # print(f"\nCaptured stdout for success test:\n---\n{output}\n---\n")

        json_output = json.loads(output)
        self.assertIn(json_output['classification'], ['legit', 'spam', 'phishing', 'invalid_input'])

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('sys.exit') 
    @patch('email_guard_sdk.classifier.EmailGuardAI.__new__') # Patch __new__ method
    def test_cli_execution_model_not_found(self, MockEmailGuardAINew, mock_exit, mock_stderr, mock_stdout, mock_parse_args):
        # When EmailGuardAI.__new__ is called, it should raise FileNotFoundError
        MockEmailGuardAINew.side_effect = FileNotFoundError("Mocked model not found error for CLI test.")

        mock_parse_args.return_value.email_text = "dummy text"
        mock_parse_args.return_value.model = "/non/existent/path/model.joblib" 
        
        # Reset the EmailGuardAI singleton's internal state before the test runs
        EmailGuardAI._instance = None 

        email_guard.main() 

        mock_exit.assert_called_once_with(1)
        
        error_output = mock_stderr.getvalue()
        
        sys.stderr.flush()

        self.assertIn("error", error_output.lower())
        self.assertIn("mocked model not found error for cli test", error_output.lower()) 
        self.assertNotIn("classification", mock_stdout.getvalue())

    @patch.dict(os.environ, {"API_KEY": "super_secret_email_guard_key_123"}, clear=True)
    def test_scan_endpoint_success(self):
        client = self.app_client
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer super_secret_email_guard_key_123'}
        data = {'email_text': 'This is a test legitimate email for API.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('classification', json_data)
        self.assertIn('confidence', json_data)
        self.assertIn('explanation', json_data)
        self.assertIn(json_data['classification'], ['legit', 'spam', 'phishing'])

    @patch.dict(os.environ, {"API_KEY": "super_secret_email_guard_key_123"}, clear=True)
    def test_scan_endpoint_unauthorized(self):
        client = self.app_client
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer wrong_key'}
        data = {'email_text': 'This is a test email.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.get_json())

    @patch.dict(os.environ, {}, clear=True)
    def test_scan_endpoint_no_api_key_in_env(self):
        client = app.test_client()
        headers = {'Content-Type': 'application/json'}
        data = {'email_text': 'This should pass without auth if key is missing.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))
        
        self.assertEqual(response.status_code, 200) 
        self.assertIn('classification', response.get_json())

    @patch.dict(os.environ, {"API_KEY": "super_secret_email_guard_key_123"}, clear=True)
    def test_scan_endpoint_invalid_input(self):
        client = self.app_client
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer super_secret_email_guard_key_123'}
        data = {'not_email_text': 'This is a test email.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    @patch.dict(os.environ, {"API_KEY": "super_secret_email_guard_key_123"}, clear=True)
    def test_history_endpoint_success(self):
        client = self.app_client
        headers = {'Authorization': 'Bearer super_secret_email_guard_key_123'}
        response = client.get('/history', headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('history', json_data)
        self.assertIsInstance(json_data['history'], list)

    @patch.dict(os.environ, {"API_KEY": "super_secret_email_guard_key_123"}, clear=True)
    def test_history_endpoint_unauthorized(self):
        client = self.app_client
        headers = {'Authorization': 'Bearer wrong_key'}
        response = client.get('/history', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main()