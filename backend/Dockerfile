# backend/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire SDK package source code
COPY email_guard_sdk email_guard_sdk/

# --- IMPORTANT CHANGE HERE ---
# Explicitly copy the trained model file into the SDK's model directory within the container
# This ensures it's always at /app/email_guard_sdk/model/email_guard_model.joblib
COPY email_guard_sdk/model/email_guard_model.joblib email_guard_sdk/model/email_guard_model.joblib
# --- END IMPORTANT CHANGE ---

# Copy setup.py and README.md from the build context root to the /app directory
COPY setup.py /app/
COPY README.md /app/

# Install the SDK from the current working directory (/app)
RUN pip install --no-cache-dir .

# Copy the backend application code
COPY backend/app.py .
COPY data/SMSSpamCollection data/
COPY data/phishing_email_dataset.csv data/
COPY data/spam.csv data/

# Download NLTK data (essential for your AI model's preprocessing)
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]