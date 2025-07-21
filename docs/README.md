# EmailGuard: AI-Powered Spam & Phishing Detection Toolkit

![EmailGuard Architecture Diagram](docs/architecture.png)

## Overview

EmailGuard is a comprehensive toolkit designed to classify emails as "legitimate," "spam," or "phishing" using a machine learning model. It offers a flexible solution with both a command-line interface (CLI) for quick, on-demand scanning and a robust Flask-based RESTful API for seamless integration into larger applications or services.

Built with `scikit-learn` and `Flask`, EmailGuard aims to provide a reliable first line of defense against unwanted and malicious emails by leveraging natural language processing and machine learning techniques.

## Features

* **Intelligent Classification:** Uses a trained machine learning model to accurately categorize emails.
* **Dual Interface:** Access functionality via a simple command-line tool or a RESTful API.
* **Robust Text Preprocessing:** Handles noisy email data by cleaning, normalizing, and transforming text for optimal model performance.
* **Comprehensive Documentation:** Detailed guides for setup, usage, and internal architecture.
* **Security Considerations:** Built with an awareness of security best practices, including API key authentication.

## Live Demo

* **Frontend (Web App):** [YOUR_DEPLOYED_FRONTEND_URL_HERE] (e.g., Vercel URL)
* **Backend (API Base URL):** [YOUR_DEPLOYED_BACKEND_URL_HERE] (e.g., Render/Railway URL)

## Getting Started

To get EmailGuard up and running on your local machine, follow these steps.

### 1. Clone the Repository

```bash
git clone https://github.com/Nohayla10/email-guard.git
cd email_guard

###2. Create and Activate a Virtual Environment
python -m venv venv
# On Windows: .\venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Download NLTK Data
# The project uses NLTK for text preprocessing. This step is often handled automatically on first run, but you can manually ensure the data is present:
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"


### 5. Train the AI Model
# The machine learning model needs to be trained and saved before you can use the CLI or API.n
# From the project's root directory, run:
python ai/email_guard_model.py


## Usage

### Command Line Interface (CLI)
```Scan an email directly from your terminal:

python email_guard.py "Your Amazon order has shipped. Track it here: [amazon.com/track/123](https://amazon.com/track/123)"

``` The output will be a JSON-formatted string with classification, confidence, and explanation.

### RESTful API
#### 1 . Run the Backend Server Locally: 
python backend/app.py
``` The server will typically run on http://127.0.0.1:5000/ 
#### 2 . API Endpoints: 
/ (GET): Health check.

/scan (POST): Classifies email text. Requires email_text in JSON body and Authorization: Bearer YOUR_API_KEY header (if API_KEY is set).

/history (GET): Retrieves recent scan history. Requires Authorization: Bearer YOUR_API_KEY header (if API_KEY is set).

## Project Structure
email_guard/
├── ai/
│   ├── __init__.py
│   ├── email_guard.py            # Defines the EmailGuardAI class and preprocessing logic
│   └── email_guard_model.py      # Script to train and save the AI model
│   └── email_guard_model.joblib  # Trained model file (generated after training)
├── backend/
│   ├── __init__.py
│   └── app.py                    # Flask API application
├── data/
│   ├── spam.csv
│   ├── phishing_email_dataset.csv
│   └── SMSSpamCollection
├── docs/
│   ├── architecture.png          # Generated architecture diagram image
│   └── README.md                 # This file
│   └── security_notes.md         # Document detailing security considerations
├── frontend/        # frontend application
│   └── web/                      # web frontend (e.g., React app)
│       ├── public/
│       ├── src/
│       └── package.json
│       └── ... (other frontend files)
├── tests/
│   ├── __init__.py
│   └── test_email_guard.py       # Unit tests for the entire project
├── .env                          # Environment variables (e.g., API_KEY) 
├── email_guard.py                # Main CLI tool for email classification
├── requirements.txt              # Python project dependencies
└── reflection.md                 # My reflection on the project journey

## Testing 
python -m unittest tests/test_email_guard.py