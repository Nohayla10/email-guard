import argparse
import json
import os
import sys

try:
    from email_guard_sdk.classifier import EmailGuardAI
except ImportError as e:
    error_message = {
        "error": f"Error importing EmailGuardAI from SDK: {e}. Ensure 'email_guard_sdk' is correctly installed.",
        "suggestion": "Please run 'pip install -e .' from the project root to install the SDK, or ensure your virtual environment is active."
    }
    print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True)
    sys.stderr.flush()
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Smart Email Guardian: AI-Powered Spam & Phishing Detection Toolkit CLI"
    )
    parser.add_argument(
        "email_text",
        type=str,
        help="The raw email text to classify."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to the pre-trained AI model file (optional, SDK loads from package by default). "
             "Use this if you want to specify a model file outside the SDK's default location."
    )

    args = parser.parse_args()

    try:
        email_guard_instance = EmailGuardAI(model_path=args.model)
        result = email_guard_instance.classify_email(args.email_text)
        print(json.dumps(result, indent=2), flush=True)
        sys.stdout.flush()
        sys.exit(0)
    except FileNotFoundError as e:
        error_message = {
            "error": str(e),
            "suggestion": "Ensure the model file exists at the specified path or within the installed SDK package. "
                          "Run 'python ai/email_guard_model.py' from the project root to generate/update it."
        }
        print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True)
        sys.stderr.flush()
        sys.exit(1)
    except Exception as e:
        error_message = {
            "error": f"An unexpected error occurred: {e}"
        }
        print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True)
        sys.stderr.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()