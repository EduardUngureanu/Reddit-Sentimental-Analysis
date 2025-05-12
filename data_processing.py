import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import sqlite3
import database_helper

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))

def process_reddit_text(text: str) -> str:
    """
    Processes text (specific to reddit, but not necessarily) and returns the processed text.

    Applied processes: 
    - make lowercase
    - remove URLs
    - remove usernames ( u/user )
    - remove extra whitespaces (eg. converts multiple spaces to 1)
    - remove punctuation
    - tokenize
    - remove stopwords

    Args:
        text (str) : Text to be processed.
    Returns:
        str : Processed text.
    """
    # make lowercase
    text = text.lower()
    # remove URLs
    text = re.sub(r'http\S+', '', text)
    # remove usernames ( u/user )
    text = re.sub(r'u/\w+', '', text)
    # remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    # remove punctuation
    text = re.sub(r'[^\w\s$]', '', text)
    # tokenize
    tokens = word_tokenize(text)
    # remove stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]
    # rejoin tokens
    processed_text = ' '.join(filtered_tokens)

    return processed_text

def process_database(reddit_db_conn: sqlite3.Connection):
    """
    Iterate over the `posts` and `comments` tables in the database and process the text, then inserts it under the new column `processed_text`.

    If the column already exists, it will rise a warning and continue. It will overwrite existing values.

    The text for posts will be a concatenation of the tile and body of the post.
    
    Args:
        reddit_db_conn (sqlite3.Connection) : Database connection, not a cursor due to needing 2 cursors to read and write simultaneously.
    """
    read_cursor = reddit_db_conn.cursor()
    write_cursor = reddit_db_conn.cursor()

    print("############# Processing posts #############")
    database_helper.add_new_column(write_cursor, 'posts', 'processed_text', 'TEXT')
    read_cursor.execute("SELECT rowid, * FROM posts")
    for row in read_cursor:
        write_cursor.execute("UPDATE posts SET processed_text = ? WHERE rowid = ?", (process_reddit_text(f"{row[4]} {row[5]}"), row[0]))

    print("############# Processing comments #############")
    database_helper.add_new_column(write_cursor, 'comments', 'processed_text', 'TEXT')
    read_cursor.execute("SELECT rowid, * FROM comments")
    for row in read_cursor:
        write_cursor.execute("UPDATE comments SET processed_text = ? WHERE rowid = ?", (process_reddit_text(row[6]), row[0]))

    read_cursor.close()
    write_cursor.close()