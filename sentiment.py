import database_helper
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import re
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import GoEmotions
import sentiment140
import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
import sqlite3

from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression

Sentiment140_model = joblib.load('Sentiment140_model.pkl')
GoEmotions_model = joblib.load('GoEmotions_model.pkl')

def process_text_GoEmotions(text):
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

def process_text_Sentiment140(text):
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

def Sentiment140_sentiment(text):
    cleaned_text = process_text_Sentiment140(text)
    sentiment = Sentiment140_model.predict([cleaned_text])
    return sentiment[0]

def GoEmotions_sentiment(text):
    cleaned_text = process_text_GoEmotions(text)
    sentiment = GoEmotions_model.predict([cleaned_text])
    return sentiment[0]

def assign_sentiment(reddit_db_con):
    reddit_db_con.row_factory = sqlite3.Row

    read_cursor = reddit_db_con.cursor()
    write_cursor = reddit_db_con.cursor()

    print("############# Processing posts #############")
    database_helper.add_new_column(write_cursor, 'posts', 'Sentiment140_score', 'INTEGER')
    database_helper.add_new_column(write_cursor, 'posts', 'GoEmotions_score', 'INTEGER')
    read_cursor.execute("SELECT rowid, title, body FROM posts")
    for row in read_cursor:
        text = f"{row['title']} {row['body']}"
        s140 = int(Sentiment140_sentiment(text))
        ge = int(GoEmotions_sentiment(text))
        write_cursor.execute("UPDATE posts SET Sentiment140_score = ?, GoEmotions_score = ? WHERE rowid = ?", (s140, ge, row['rowid']))
    
    reddit_db_con.commit()

    print("############# Processing comments #############")
    database_helper.add_new_column(write_cursor, 'comments', 'Sentiment140_score', 'INTEGER')
    database_helper.add_new_column(write_cursor, 'comments', 'GoEmotions_score', 'INTEGER')
    read_cursor.execute("SELECT rowid, body FROM comments")
    for row in read_cursor:
        s140 = int(Sentiment140_sentiment(row['body']))
        ge = int(GoEmotions_sentiment(row['body']))
        write_cursor.execute("UPDATE comments SET Sentiment140_score = ?, GoEmotions_score = ? WHERE rowid = ?", (s140, ge, row['rowid']))

    reddit_db_con.commit()

    read_cursor.close()
    write_cursor.close()

def test(reddit_db_con):
    reddit_db_con.row_factory = sqlite3.Row

    cursor = reddit_db_con.cursor()

    # cursor.execute("ALTER TABLE posts DROP COLUMN Sentiment140_score;")
    # cursor.execute("ALTER TABLE posts DROP COLUMN GoEmotions_score;")

    # cursor.execute("ALTER TABLE comments DROP COLUMN Sentiment140_score;")
    # cursor.execute("ALTER TABLE comments DROP COLUMN GoEmotions_score;")

    # reddit_db_con.commit()

    # read_cursor = reddit_db_con.cursor()
    # write_cursor = reddit_db_con.cursor()

    # read_cursor.execute("PRAGMA table_info(posts)")
    # for col in read_cursor.fetchall():
    #     print(dict(col))

    # read_cursor.execute("SELECT rowid, title, body, Sentiment140_score, GoEmotions_score  FROM posts")
    # row = read_cursor.fetchone()
    # text = f"{row['title']} {row['body']}"
    # print(text)
    # s140 = Sentiment140_sentiment(text)
    # print(s140)
    # ge = GoEmotions_sentiment(text)
    # print(ge)
    # print(f"{row['Sentiment140_score']} {row['GoEmotions_score']}")

    # read_cursor.close()
    # write_cursor.close()


folder = "2025-05-27_19-02-02"
reddit_db_con = database_helper.get_reddit_db_connection(f"reddit_data\\{folder}\\data.db")
assign_sentiment(reddit_db_con)
# test(reddit_db_con)

reddit_db_con.commit()
reddit_db_con.close()