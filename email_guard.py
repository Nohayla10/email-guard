
import argparse
import json
import os
import sys


project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from ai.email_guard import EmailGuardAI

def main():
    parser = argparse.ArgumentParser(description="Smart Email Guardian: AI-Powered Spam & Phishing Detection Toolkit CLI")
    parser.add_argument("email_text", type=str, help="The raw email text to classify.")
    parser.add_argument("--model", type=str, default="ai/email_guard_model.joblib", # Default path relative to project root
                        help="Path to the pre-trained AI model file (e.g., ai/email_guard_model.joblib).")

    args = parser.parse_args()

    try:
        ai_guardian = EmailGuardAI(model_path=args.model)
        result = ai_guardian.classify_email(args.email_text)
        print(json.dumps(result, indent=2))
    except FileNotFoundError as e:
        error_message = {
            "error": str(e),
            "suggestion": "Ensure the model file exists at the specified path. Run 'python ai/email_guard_model.py' to generate it if using the scikit-learn approach."
        }

        print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True) # Added flush=True
        sys.exit(1)
    except Exception as e:
        error_message = {
            "error": f"An unexpected error occurred: {e}"
        }
      
        print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True) # Added flush=True
        sys.exit(1)

if __name__ == "__main__":
    main()