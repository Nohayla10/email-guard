
import pandas as pd
import os
import joblib
import sys
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


print("Checking NLTK resources...")
download_needed = False
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    download_needed = True
    print("NLTK 'stopwords' not found.")
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    download_needed = True
    print("NLTK 'wordnet' not found.")

if download_needed:
    print("Downloading missing NLTK resources. This may take a moment...")
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("NLTK resources downloaded successfully.")
    except Exception as e:
        print(f"Error downloading NLTK resources: {e}")
        print("Please try running 'python -c \"import nltk; nltk.download(\'stopwords\'); nltk.download(\'wordnet\')\"' manually.")
        sys.exit(1)


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.email_guard import preprocess_text # <--- IMPORTANT: Use the one from ai/email_guard.py

# --- Main Model Training Function ---
def train_and_save_model():
    data_path_email_spam = 'data/spam.csv' # Your original email spam dataset
    data_path_phishing = 'data/phishing_email_dataset.csv' # Your phishing dataset
    data_path_sms_spam = 'data/SMSSpamCollection' # NEW: SMS Spam dataset

    combined_dfs = []

    # --- Load Original Email Spam Dataset (spam.csv) ---
    df_email_spam = pd.DataFrame()
    if os.path.exists(data_path_email_spam):
        print(f"Loading email spam dataset from {data_path_email_spam}...")
        try:
            df_email_spam = pd.read_csv(data_path_email_spam, encoding='latin-1', sep=',')
            df_email_spam = df_email_spam[['v1', 'v2']]
            df_email_spam.columns = ['label', 'text']
            df_email_spam['label'] = df_email_spam['label'].map({'ham': 'legit', 'spam': 'spam'})
            df_email_spam.dropna(subset=['text', 'label'], inplace=True)
            df_email_spam = df_email_spam[df_email_spam['text'].str.strip().astype(bool)]
            print(f"Email spam dataset loaded: {len(df_email_spam)} examples.")
            combined_dfs.append(df_email_spam)
        except Exception as e:
            print(f"Error loading email spam CSV: {e}")
            print("Skipping original email spam dataset.")
    else:
        print(f"Email spam dataset not found at {data_path_email_spam}.")

    # --- Load Phishing Email Dataset (phishing_email_dataset.csv) ---
    df_phishing = pd.DataFrame()
    if os.path.exists(data_path_phishing):
        print(f"Loading phishing dataset from {data_path_phishing}...")
        try:
            df_phishing = pd.read_csv(data_path_phishing, encoding='utf-8')
            df_phishing = df_phishing[['Email Text', 'Email Type']]
            df_phishing.columns = ['text', 'label']
            df_phishing['label'] = df_phishing['label'].map({
                'Phishing Email': 'phishing',
                'Safe Email': 'legit'
            })

            df_phishing.dropna(subset=['text', 'label'], inplace=True)
            df_phishing = df_phishing[df_phishing['text'].str.strip().astype(bool)]
            print(f"Phishing dataset loaded: {len(df_phishing)} examples.")
            combined_dfs.append(df_phishing)
        except Exception as e:
            print(f"Error loading phishing CSV: {e}")
            print("Skipping phishing dataset.")
    else:
        print(f"Phishing dataset not found at {data_path_phishing}.")

    # --- NEW: Load SMS Spam Collection (SMSSpamCollection) ---
    df_sms_spam = pd.DataFrame()
    if os.path.exists(data_path_sms_spam):
        print(f"Loading SMS spam dataset from {data_path_sms_spam}...")
        try:
            df_sms_spam = pd.read_csv(data_path_sms_spam, sep='\t', header=None, names=['label', 'text'], encoding='latin-1')
            df_sms_spam['label'] = df_sms_spam['label'].map({'ham': 'legit', 'spam': 'spam'})
            df_sms_spam.dropna(subset=['text', 'label'], inplace=True)
            df_sms_spam = df_sms_spam[df_sms_spam['text'].str.strip().astype(bool)]
            print(f"SMS spam dataset loaded: {len(df_sms_spam)} examples.")
            combined_dfs.append(df_sms_spam)
        except Exception as e:
            print(f"Error loading SMS spam dataset: {e}")
            print("Skipping SMS spam dataset.")
    else:
        print(f"SMS spam dataset not found at {data_path_sms_spam}.")


    # --- Combine All Datasets ---
    if combined_dfs:
        df = pd.concat(combined_dfs, ignore_index=True)
        initial_len = len(df)
        df.drop_duplicates(subset=['text'], inplace=True)
        print(f"Removed {initial_len - len(df)} duplicate entries.")
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"Combined and deduplicated dataset loaded: {len(df)} examples found.")
    else:
        print("No external datasets loaded. Using dummy data for training.")
        texts = [
            "Hello, your order has been shipped. Track it here: example.com/track123", # Legit
            "You won a million dollars! Click here to claim: tinyurl.com/freecash", # Spam
            "Urgent: Verify your bank account details or it will be suspended. Login at: fakebank.com/login", # Phishing
            "Meeting reminder for tomorrow at 10 AM. Agenda attached.", # Legit
            "Your Netflix account is on hold. Update payment info now: netflix-support.info/update", # Phishing
            "Exclusive offer: Get rich quick! Visit: scam-site.net", # Spam
            "Regarding your recent query, we have updated your ticket.", # Legit
            "Dear customer, you have received a new message from HMRC. Follow the link to view: hmrc-online.co.uk", # Phishing
            "Congratulations, you've been selected for a free gift card. Click here!", # Spam
            "Project status update: all tasks are proceeding as planned." # Legit
        ]
        labels = [
            "legit", "spam", "phishing", "legit", "phishing",
            "spam", "legit", "phishing", "spam", "legit"
        ]
        df = pd.DataFrame({'text': texts, 'label': labels})

    print("\nLabel distribution after combining:")
    print(df['label'].value_counts())

    if len(df) == 0:
        print("No data available for training. Exiting.")
        return

    texts = df['text'].tolist()
    labels = df['label'].tolist()

    # Split data
    try:
        X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42, stratify=labels)
    except ValueError as e:
        print(f"Warning: Error splitting data with stratification ({e}). This usually means one of your classes has too few samples for the test_size (e.g., less than 2 if test_size=0.2).")
        print("Proceeding without stratification. Consider adjusting test_size or getting more data for minority classes.")
        X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # Create a pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, preprocessor=preprocess_text)),
        ('classifier', LogisticRegression(max_iter=1000, solver='liblinear', class_weight='balanced'))
    ])

    print("\nTraining model...")
    pipeline.fit(X_train, y_train)
    print("Model trained.")

    # Evaluate
    print("\nEvaluating model performance on test set:")
    y_pred = pipeline.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    print(f"\nOverall Metrics on Test Set:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision (weighted): {precision:.4f}")
    print(f"Recall (weighted): {recall:.4f}")
    print(f"F1-Score (weighted): {f1:.4f}")

    # Save the model
    model_dir = 'ai'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_path = os.path.join(model_dir, 'email_guard_model.joblib')
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved to {model_path}")

# --- Entry point of the script ---
if __name__ == "__main__":
    train_and_save_model()