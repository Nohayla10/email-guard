
import re
import string
import nltk
from nltk.corpus import stopwords


try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("NLTK 'stopwords' resource not found. Downloading...")
    nltk.download('stopwords')
    print("NLTK 'stopwords' downloaded successfully.")

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text) 
    text = re.sub(r'\d+', '', text) 
    text = ' '.join([word for word in text.split() if word not in stop_words]) 
    return text

