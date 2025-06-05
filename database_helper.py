import sqlite3

def get_reddit_db_connection(reddit_db_path: str):
    """
    Connect to a databases (will create one if it doesn't exist) and automatically forms the tables for posts and comments:

    posts:
        rowid (primary key), company, subreddit, post_id, title, body, is_self, created_utc, link

    comments:
        rowid (primary key), company, subreddit, post_id, parent_id, comment_id, body, created_utc, link

    Args:
        reddit_db (str) : Path of the database file.
    Returns:
        sqlite3.Connection : Connection to the database, with tables already created.
    """
    reddit_db_con = sqlite3.connect(reddit_db_path, autocommit=True)

    cur = reddit_db_con.cursor()

    post_table_command = "CREATE TABLE IF NOT EXISTS posts(" \
    "company TEXT, " \
    "subreddit TEXT, " \
    "post_id TEXT, " \
    "title TEXT, " \
    "body TEXT, " \
    "is_self BOOLEAN, " \
    "created_utc INTEGER, " \
    "link TEXT," \
    "upvote_ratio REAL," \
    "score INTEGER)"

    cur.execute(post_table_command)

    comment_table_command = "CREATE TABLE IF NOT EXISTS comments(" \
    "company TEXT, " \
    "subreddit TEXT, " \
    "post_id TEXT, " \
    "parent_id TEXT, " \
    "comment_id TEXT, " \
    "body TEXT, " \
    "created_utc INTEGER, " \
    "link TEXT, " \
    "score INTEGER)"

    cur.execute(comment_table_command)

    cur.close()

    return reddit_db_con

def insert_into_posts(reddit_db_cur: sqlite3.Cursor, company: str, subreddit: str, post_id: str, title: str, body: str, is_self: bool, created_utc: int, link: str, upvote_ratio: float, score: int):
    """
    Insert a new entry into the `posts` table
    Args:
        reddit_db_con (sqlite3.Cursor) : Cursor for the reddit database.
        Other : Post data, mostly self explanatory.
    """

    # command = f"INSERT INTO posts VALUES({company},{subreddit},{post_id},{title},{body},{created_utc},{link})"
    # reddit_db_cur.execute(command)

    reddit_db_cur.execute("INSERT INTO posts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (company, subreddit, post_id, title, body, is_self, created_utc, link, upvote_ratio, score))

def insert_into_comments(reddit_db_cur: sqlite3.Cursor, company: str, subreddit: str, post_id: str, parent_id: str, comment_id: str, body: str, created_utc: int, link: str, score: int):
    """
    Insert a new entry into the `comments` table
    Args:
        reddit_db_con (sqlite3.Cursor) : Cursor for the reddit database.
        Other : Comment data, mostly self explanatory.
    """

    # command = f"INSERT INTO comments VALUES({company},{subreddit},{post_id},{parent_id},{comment_id},{body},{created_utc},{link})"
    # reddit_db_cur.execute(command)

    reddit_db_cur.execute("INSERT INTO comments VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (company, subreddit, post_id, parent_id, comment_id, body, created_utc, link, score))

def  add_new_column(cur: sqlite3.Cursor, table: str, name: str, type: str):
    """
    Add a new column to the specified table

    Args:
        cur (sqlite3.Cursor): Database cursor.
        table  (str): Table name.
        name (str): Name or header of the column to be added.
        type (str): Data type, must be a valid sql3lite data type.
    """
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {name} {type}")
    except sqlite3.OperationalError:
        print(f"Column '{name}' might already exist. Skipping ALTER TABLE.")