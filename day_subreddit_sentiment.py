import database_helper
import sqlite3
import json

def get_subreddits(cursor):
    cursor.execute("SELECT DISTINCT subreddit FROM posts")
    return [row[0] for row in cursor.fetchall()]

folder = "2025-05-27_19-02-02"
reddit_db_con = database_helper.get_reddit_db_connection(f"reddit_data\\{folder}\\data.db")
reddit_db_con.row_factory = sqlite3.Row
cursor = reddit_db_con.cursor()

subreddits = get_subreddits(cursor)
print(f"Subreddits found: {subreddits}")

results = {}

for subreddit in subreddits:
    print(f"### Processing subreddit: {subreddit}")

    cursor.execute("SELECT SUM(score) FROM posts WHERE subreddit = ?", (subreddit,))
    result = cursor.fetchone()
    posts_score = result[0] if result[0] is not None else 0
    print(f"Post score: {posts_score}")

    cursor.execute("SELECT SUM(score) FROM comments WHERE subreddit = ?", (subreddit,))
    result = cursor.fetchone()
    comment_score = result[0] if result[0] is not None else 0
    print(f"Comment score: {comment_score}")

    total_score = posts_score + comment_score
    print(f"TOTAL score: {total_score}")

    Vader_weighted = 0.0
    Sentiment140_weighted = 0.0
    GoEmotions_weighted = 0.0

    # Process posts
    cursor.execute("SELECT score, Sentiment140_score, GoEmotions_score, Vader_score FROM posts WHERE subreddit = ?", (subreddit,))
    for row in cursor:
        score = row['score']
        if total_score > 0 and score > 0:
            weight = score / total_score
            Vader_weighted += weight * row['Vader_score']
            Sentiment140_weighted += weight * row['Sentiment140_score']
            GoEmotions_weighted += weight * row['GoEmotions_score']

    # Process comments
    cursor.execute("SELECT score, Sentiment140_score, GoEmotions_score, Vader_score FROM comments WHERE subreddit = ?", (subreddit,))
    for row in cursor:
        score = row['score']
        if total_score > 0 and score > 0:
            weight = score / total_score
            Vader_weighted += weight * row['Vader_score']
            Sentiment140_weighted += weight * row['Sentiment140_score']
            GoEmotions_weighted += weight * row['GoEmotions_score']

    print(f"Weighted Vader sentiment: {Vader_weighted}")
    print(f"Weighted Sentiment140 sentiment: {Sentiment140_weighted}")
    print(f"Weighted GoEmotions sentiment: {GoEmotions_weighted}")
    print("--------------------------------------------------------------------------")

    results[subreddit] = {
        "total_score": total_score,
        "Vader_weighted": Vader_weighted,
        "Sentiment140_weighted": Sentiment140_weighted,
        "GoEmotions_weighted": GoEmotions_weighted
        
    }

# Save to JSON
with open(f"sentiment_results_{folder}.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

cursor.close()
reddit_db_con.close()