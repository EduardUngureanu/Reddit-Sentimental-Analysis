import praw
import json
import praw.models
import reddit_helper
from datetime import datetime
import sqlite3
import database_helper
import data_processing

# reddit = reddit_helper.get_access_to_reddit("user.json")

conn = sqlite3.connect("reddit_data/2025-05-11_16-48-23/data.db", autocommit=True)
cursor = conn.cursor()

data_processing.process_database(conn)

# if (is_self := submission.is_self):
#     print(is_self)
# print(submission.is_self)
# print(is_self)

# if not (submission_body := submission.selftext):
#     submission_body = submission.url

# permalink = submission.permalink

# print(permalink)

# print(reddit_helper.create_post_link(permalink))

# submission.comment_sort = 'best'
# submission.comment_limit = 1

# submission.comments.replace_more(limit=0)
# for comment in submission.comments.list():
#     if isinstance(comment, praw.models.MoreComments):
#         continue
#     print(comment.parent_id)

# print(submission.id)

# sub = reddit.subreddit('nvidia')

# posts = reddit_helper.probe_sub_for_top_posts(sub, 1)

# print(sub.name, "/n", sub.display_name)

# comments_list = []

# posts[0].comment_sort = 'best'
# posts[0].comment_limit = 50

# posts[0].comments.replace_more(limit = 0)
# for comment in posts[0].comments.list():
#     if isinstance(comment, praw.models.MoreComments):
#         continue
#     print(comment.score, " //// ", comment.body)

# current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print(current_datetime)

