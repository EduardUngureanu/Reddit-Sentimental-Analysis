import kagglehub
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import shutil
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

sentiment140_default = "training.1600000.processed.noemoticon.csv"
download_to = ".\\datasets\\sentiment140"
sentiment140_stemmed = "sentiment140_processed_stemmed.csv"
sentiment140_lemmatized = "sentiment140_processed_lemmatized.csv"
sentiment140_embeddings = "sentiment140_processed_embeddings.csv"

def download():
    file_path = os.path.join(download_to, sentiment140_default)
    
    if os.path.exists(file_path):
        print(f"sentiment140 already downloaded")
        return

    print(f"Downloading sentiment140...")
    try:
        path = kagglehub.dataset_download("kazanova/sentiment140")
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    try:
        os.mkdir(download_to)
        print(f"Directory '{download_to}' created successfully.")
    except FileExistsError:
        print(f"Directory '{download_to}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{download_to}'.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    try:
        os.rename(os.path.join(path, sentiment140_default), file_path)
        print(f"Downloaded to '{file_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleaning download cache")
        str = path.split("\\sentiment140")
        shutil.rmtree(str[0])
    
def read(path: str):
    try:
        with open(path, "r") as file:
            df = pd.read_csv(file, encoding='latin-1', header=None)
            df.columns = ['sentiment', 'id', 'date', 'query', 'user', 'text']

            return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def process_tweet_stemmed(text):
    stop_words = set(stopwords.words('english'))
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # @user
    text = re.sub(r'@\w+', '', text)
    # hashtags (#, but keep the word)
    text = re.sub(r'#', '', text)
    # emoji and other non-ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # lowercase convert
    text = text.lower()
    # remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    # tokenize
    tokens = word_tokenize(text)
    # stopwords
    tokens = [word for word in tokens if word not in stop_words]

    stemmer = PorterStemmer()
    stemm = [stemmer.stem(word) for word in tokens]
    # join back tokens
    cleaned_text = ' '.join(stemm)
    
    return cleaned_text

def process_tweet_lemmatized(text):
    stop_words = set(stopwords.words('english'))
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # @user
    text = re.sub(r'@\w+', '', text)
    # hashtags (#, but keep the word)
    text = re.sub(r'#', '', text)
    # emoji and other non-ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # lowercase convert
    text = text.lower()
    # remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    # tokenize
    tokens = word_tokenize(text)
    # stopwords
    tokens = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    lemm = [lemmatizer.lemmatize(word) for word in tokens]
    # join back tokens
    cleaned_text = ' '.join(lemm)
    
    return cleaned_text

def process_tweet(text):
    stop_words = set(stopwords.words('english'))
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # @user
    text = re.sub(r'@\w+', '', text)
    # hashtags (#, but keep the word)
    text = re.sub(r'#', '', text)
    # emoji and other non-ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # lowercase convert
    text = text.lower()
    # remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    # tokenize
    tokens = word_tokenize(text)
    # stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]
    # join back tokens
    cleaned_text = ' '.join(filtered_tokens)
    
    return cleaned_text

def process_tweet_embeddings(text):
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # @user
    text = re.sub(r'@\w+', '', text)
    # hashtags (#, but keep the word)
    text = re.sub(r'#', '', text)
    # emoji and other non-ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # lowercase convert
    text = text.lower()
    # remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def process(function, original, filename):
    file_path = os.path.join(download_to, filename)

    if os.path.exists(file_path):
        print(f"sentiment140 already processed")
        return

    print(f"Processing sentiment140...")
    
    df = read(os.path.join(download_to, original))
    if df is not None:
        df = df.drop(columns=['id', 'date', 'query', 'user'])
        df['sentiment'] = df['sentiment'].apply(lambda x: 1 if x == 4 else 0)

        df['clean_text'] = df['text'].apply(function)

        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"processed data saved as '{file_path}'")
    else:
        print("Couldn't read sentiment140")

def setup():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

    nltk.download('wordnet')
    download()
    process(process_tweet_stemmed, sentiment140_default, sentiment140_stemmed)
    process(process_tweet_lemmatized, sentiment140_default, sentiment140_lemmatized)
    process(process_tweet_embeddings, sentiment140_default, sentiment140_embeddings)

if __name__ == "__main__":
    setup()