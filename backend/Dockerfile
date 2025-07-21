# backend/Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY backend/app.py .
COPY ai/email_guard.py ai/
COPY ai/email_guard_model.joblib ai/
COPY data/SMSSpamCollection data/
COPY data/phishing_email_dataset.csv data/
COPY data/spam.csv data/


RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]