# email_guard.py
import argparse
import json
import os
import sys

try:
    # Attempt to import EmailGuardAI from the installed SDK package
    from email_guard_sdk.classifier import EmailGuardAI
except ImportError as e:
    # If the SDK is not installed or the import fails, print an error and exit.
    # This ensures the CLI tool provides helpful feedback if the environment isn't set up.
    error_message = {
        "error": f"Error importing EmailGuardAI from SDK: {e}. Ensure 'email_guard_sdk' is correctly installed.",
        "suggestion": "Please run 'pip install -e .' from the project root to install the SDK, or ensure your virtual environment is active."
    }
    print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True)
    sys.stderr.flush() # Explicitly flush stderr to ensure message is displayed
    sys.exit(1) # Exit with a non-zero status code to indicate an error

def main():
    """
    Main function for the EmailGuard CLI tool.
    Parses arguments, initializes the AI model, classifies email text,
    and prints the result or an error message.
    """
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
        # Initialize the EmailGuardAI model.
        # If args.model is None, the SDK will attempt to load the model from its package.
        # If args.model is provided, it will attempt to load from that specific path.
        email_guard_instance = EmailGuardAI(model_path=args.model)

        # Classify the provided email text
        result = email_guard_instance.classify_email(args.email_text)

        # Print the classification result to standard output in JSON format
        print(json.dumps(result, indent=2), flush=True)
        sys.stdout.flush() # Explicitly flush stdout to ensure message is displayed

        # Exit with a success status code
        sys.exit(0)
    except FileNotFoundError as e:
        # Handle cases where the model file is not found
        error_message = {
            "error": str(e),
            "suggestion": "Ensure the model file exists at the specified path or within the installed SDK package. "
                          "Run 'python ai/email_guard_model.py' from the project root to generate/update it."
        }
        print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True)
        sys.stderr.flush() # Explicitly flush stderr
        sys.exit(1) # Exit with an error status code
    except Exception as e:
        # Catch any other unexpected errors during classification or model loading
        error_message = {
            "error": f"An unexpected error occurred: {e}"
        }
        print(json.dumps(error_message, indent=2), file=sys.stderr, flush=True)
        sys.stderr.flush() # Explicitly flush stderr
        sys.exit(1) # Exit with an error status code

if __name__ == "__main__":
    main()