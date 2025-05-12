import globals
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))

def read_sentiment140():
    try:
        with open(globals.sentiment140_path, "r") as file:
            df = pd.read_csv(file, encoding='latin-1', header=None)
            df.columns = ['sentiment', 'id', 'date', 'query', 'user', 'text']

            return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def preprocess_tweet(text):
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # @user
    text = re.sub(r'@\w+', '', text)
    # hashtaguri (#, dar păstrează cuvântul)
    text = re.sub(r'#', '', text)
    # emoji and other non-ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # lowercase convert
    text = text.lower()
    # tokenize
    tokens = word_tokenize(text)
    # stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]
    # join back tokens
    cleaned_text = ' '.join(filtered_tokens)
    
    return cleaned_text