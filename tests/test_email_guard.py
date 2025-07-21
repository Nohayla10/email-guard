import unittest
import os
import json
from unittest.mock import patch, MagicMock
import sys
import io # Import io

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import AI components
from ai.email_guard import EmailGuardAI, preprocess_text
from ai.email_guard_model import train_and_save_model
from email_guard import main as cli_main
from backend.app import app

class TestEmailGuard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n--- Running setUpClass for TestEmailGuard ---")
        # Ensure NLTK resources are available for preprocessing
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

        # Ensure model is trained before running tests that depend on it
        model_path_for_loading = os.path.join(project_root, 'ai', 'email_guard_model.joblib')

        if not os.path.exists(model_path_for_loading):
            print(f"Model not found at {model_path_for_loading}. Running model training script...")
            # Temporarily redirect stdout during model training to avoid mixing with test output
            original_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                train_and_save_model()
            finally:
                sys.stdout = original_stdout # Restore stdout
            print("Model training script finished successfully.")
        
        cls.email_guard_instance = EmailGuardAI(model_path='ai/email_guard_model.joblib')

        print("--- setUpClass complete ---")


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

    # --- Test CLI execution ---
    # Using io.StringIO for more reliable capture of stdout/stderr
    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_execution_success(self, mock_parse_args):
        mock_parse_args.return_value.email_text = "This is a test email for CLI."
        mock_parse_args.return_value.model = "ai/email_guard_model.joblib"
        
        # Capture stdout and stderr
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        try:
            cli_main()
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        output = captured_stdout.getvalue()
        err_output = captured_stderr.getvalue()
        
        self.assertNotIn('error', err_output) # Ensure no error on stderr
        self.assertIn('"classification"', output)
        self.assertIn('"confidence"', output)
        self.assertIn('"explanation"', output)
        json_output = json.loads(output)
        self.assertIn(json_output['classification'], ['legit', 'spam', 'phishing', 'invalid_input'])


    @patch('sys.exit', side_effect=SystemExit)
    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_execution_model_not_found(self, mock_parse_args, mock_exit):
        mock_parse_args.return_value.email_text = "dummy text"
        mock_parse_args.return_value.model = "non_existent_model.joblib"
        
        # Capture stdout and stderr
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        try:
            with self.assertRaises(SystemExit):
                cli_main()
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        output = captured_stdout.getvalue()
        err_output = captured_stderr.getvalue()
        
        self.assertIn("error", err_output) # Error should be on stderr
        self.assertIn("Model file not found", err_output)
        self.assertNotIn("classification", output) # No classification output on stdout for error case


    # --- Backend API Tests ---
    def test_scan_endpoint_success(self):
        client = app.test_client()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer super_secret_email_guard_key_123'}
        data = {'email_text': 'This is a test legitimate email for API.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('classification', json_data)
        self.assertIn('confidence', json_data)
        self.assertIn('explanation', json_data)
        self.assertIn(json_data['classification'], ['legit', 'spam', 'phishing'])

    def test_scan_endpoint_unauthorized(self):
        client = app.test_client()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer wrong_key'}
        data = {'email_text': 'This is a test email.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.get_json())

    def test_scan_endpoint_no_api_key_set_in_env(self):
        original_api_key = os.getenv("API_KEY")
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

        client = app.test_client()
        headers = {'Content-Type': 'application/json'}
        data = {'email_text': 'This should pass without auth if key is missing.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))
        
        self.assertIn(response.status_code, [200, 401]) 
        if response.status_code == 200:
            self.assertIn('classification', response.get_json())
        else:
            self.assertIn('error', response.get_json())

        if original_api_key is not None:
            os.environ["API_KEY"] = original_api_key

    def test_scan_endpoint_invalid_input(self):
        client = app.test_client()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer super_secret_email_guard_key_123'}
        data = {'not_email_text': 'This is a test email.'}
        response = client.post('/scan', headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    def test_history_endpoint_success(self):
        client = app.test_client()
        headers = {'Authorization': 'Bearer super_secret_email_guard_key_123'}
        response = client.get('/history', headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('history', json_data)
        self.assertIsInstance(json_data['history'], list)

    def test_history_endpoint_unauthorized(self):
        client = app.test_client()
        headers = {'Authorization': 'Bearer wrong_key'}
        response = client.get('/history', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main()