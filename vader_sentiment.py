import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
import database_helper
import sqlite3
import re

def clean_for_vader(text):
    # Optional: Remove URLs and Reddit artifacts
    text = re.sub(r"http\S+", "", text)  # Remove links
    text = re.sub(r"&amp;", "&", text)    # Fix Reddit encoding
    return text.strip()

def assign_sentiment(reddit_db_con):
    reddit_db_con.row_factory = sqlite3.Row

    sia = SentimentIntensityAnalyzer()

    read_cursor = reddit_db_con.cursor()
    write_cursor = reddit_db_con.cursor()

    print("############# Processing posts #############")
    database_helper.add_new_column(write_cursor, 'posts', 'Vader_score', 'REAL')  # Vader returns float

    read_cursor.execute("SELECT rowid, title, body FROM posts")
    for row in read_cursor:
        text = f"{row['title']} {row['body']}"
        vader = sia.polarity_scores(clean_for_vader(text))['compound']

        write_cursor.execute(
            "UPDATE posts SET Vader_score = ? WHERE rowid = ?",
            (vader, row['rowid'])
        )
    
    reddit_db_con.commit()

    print("############# Processing comments #############")
    database_helper.add_new_column(write_cursor, 'comments', 'Vader_score', 'REAL')

    read_cursor.execute("SELECT rowid, body FROM comments")
    for row in read_cursor:
        text = row['body']
        vader = sia.polarity_scores(clean_for_vader(text))['compound']

        write_cursor.execute(
            "UPDATE comments SET Vader_score = ? WHERE rowid = ?",
            (vader, row['rowid'])
        )

    reddit_db_con.commit()

    read_cursor.close()
    write_cursor.close()

folder = "2025-05-27_19-02-02"
reddit_db_con = database_helper.get_reddit_db_connection(f"reddit_data\\{folder}\\data.db")
assign_sentiment(reddit_db_con)
# test(reddit_db_con)

reddit_db_con.commit()
reddit_db_con.close()