import reddit_helper
import database_helper
import os
import time
import logging
from datetime import datetime

reddit = reddit_helper.get_access_to_reddit("user.json")

main_folder = "reddit_data"

for subfolder in os.listdir(main_folder):
    full_path = os.path.join(main_folder, subfolder)
    if os.path.isdir(full_path):
        time_now = datetime.now().strftime("%H-%M-%S")
        print(f"[{time_now}] Processing folder: {full_path}")

        reddit_db_con = database_helper.get_reddit_db_connection(f"{full_path}/data.db")

        # read_cursor = reddit_db_con.cursor()
        # write_cursor = reddit_db_con.cursor()

        # print("############# Adding to posts #############")
        # database_helper.add_new_column(write_cursor, "posts", "upvote_ratio", "REAL")
        # database_helper.add_new_column(write_cursor, "posts", "score", "INTEGER")
        # read_cursor.execute("SELECT rowid, post_id FROM posts")
        # for row in read_cursor:
        #     print(f"Processing {row[0]} - {row[1]}")
        #     post = reddit.submission(id = row[1])
        #     upvote_ratio = post.upvote_ratio
        #     score = post.score
        #     write_cursor.execute("UPDATE posts SET upvote_ratio = ?, score = ? WHERE rowid = ?", (upvote_ratio, score, row[0]))

        # read_cursor.close()
        # write_cursor.close()

        read_cursor = reddit_db_con.cursor()
        write_cursor = reddit_db_con.cursor()

        t = 0

        print("############# Adding to comments #############")
        database_helper.add_new_column(write_cursor, 'comments', 'score', 'INTEGER')

        read_cursor.execute("SELECT COUNT(*) FROM comments WHERE score IS NULL")
        nr = read_cursor.fetchone()[0]

        while nr > 0:
            try:
                read_cursor.execute("SELECT rowid, comment_id FROM comments WHERE score IS NULL")
                for row in read_cursor:
                    time_now = datetime.now().strftime("%H-%M-%S")
                    comment = reddit.comment(id = row[1])
                    score = comment.score
                    print(f"[{time_now}] Processing {row[0]} - {row[1]}, score = {score}")
                    time.sleep(0.2)
                    write_cursor.execute("UPDATE comments SET score = ? WHERE rowid = ?", (score, row[0]))
                    reddit_db_con.commit()

            except Exception as e:
                print("An error occurred, retrying after 2min: ", e)
                time.sleep(120)

            read_cursor.execute("SELECT COUNT(*) FROM comments WHERE score IS NULL")
            nr = read_cursor.fetchone()[0]
        
        read_cursor.close()
        write_cursor.close()

        reddit_db_con.close()
