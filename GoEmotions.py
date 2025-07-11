import kagglehub
from huggingface_hub import hf_hub_download
import pandas as pd
import os
import re
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

download_to = ".\\datasets\\GoEmotions"

repo_id = "spacesedan/goemotions-5point-sentiment"
train_default = "data/train-00000-of-00001.parquet"
test_default = "data/validation-00000-of-00001.parquet"
train = "train.csv"
test = "test.csv"
train_stemmed = "train_stemmed.csv"
test_stemmed = "test_stemmed.csv"
train_lemmatized = "train_lemmatized.csv"
test_lemmatized = "test_lemmatized.csv"
train_embeddings = "train_embeddings.csv"
test_embeddings = "test_embeddings.csv"

def download():
    path = os.path.join(download_to, train)
    if os.path.exists(path):
        print(f"Train dataset already downloaded")
    else:
        df = pd.read_parquet(hf_hub_download(repo_id=repo_id, filename=train_default, repo_type="dataset"))
        df.to_csv(path, index=False)
        print(f"Downloaded train dataset to {path}")

    path = os.path.join(download_to, test)
    if os.path.exists(path):
        print(f"Test dataset already downloaded")
    else:
        df = pd.read_parquet(hf_hub_download(repo_id=repo_id, filename=test_default, repo_type="dataset"))
        df.to_csv(path, index=False)
        print(f"Downloaded test dataset to {path}")

def process_text_stemmed(text):
    stop_words = set(stopwords.words('english'))
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # remove usernames ( u/user )
    text = re.sub(r'u/\w+', '', text)
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

def process_text_lemmatized(text):
    stop_words = set(stopwords.words('english'))
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # remove usernames ( u/user )
    text = re.sub(r'u/\w+', '', text)
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

def process_text_embeddings(text):
    # URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # lowercase convert
    text = text.lower()
    # remove extra whitespaces
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    
    return cleaned_text

def process(function, original, filename):
    file_path = os.path.join(download_to, filename)
    if os.path.exists(file_path):
        print(f"{original} already processed -> {filename}")
    else:
        print(f"Processing {original}...")
        df = pd.read_csv(os.path.join(download_to, original))
        df['clean_text'] = df['text'].apply(function)

        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"processed data saved as '{file_path}'")

def setup():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

    nltk.download('wordnet')
    download()
    process(process_text_stemmed, train, train_stemmed)
    process(process_text_stemmed, test, test_stemmed)
    process(process_text_lemmatized, train, train_lemmatized)
    process(process_text_lemmatized, test, test_lemmatized)
    process(process_text_embeddings, train, train_embeddings)
    process(process_text_embeddings, test, test_embeddings)

if __name__ == "__main__":
    setup()