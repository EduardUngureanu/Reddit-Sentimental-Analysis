import praw.models
import globals
import pandas as pd
import re
import praw
import json

from typing import List, Dict, Any

def get_access_to_reddit(user_file_path: str) -> praw.Reddit:
    """
    Creates a reddit connection instance. The user file needs to have those attributes and be JSON formatted:

    {"client_id" : "...",

    "client_secret" : "...",

    "username" : "...",

    "password" : "...",

    "user_agent" : "..."}

    Args:
        user_file_path(str) : path to the user file, JSON formatted.
    Returns:
        praw.Reddit : .Reddit instance.
    """
    with open(user_file_path, "r") as f:
        user = json.load(f)

    reddit = praw.Reddit(
        client_id = user["client_id"],
        client_secret = user["client_secret"],
        username = user["username"],
        password = user["password"],
        user_agent = user["user_agent"]
        )
    return reddit

def probe_sub_for_top_posts(sub: praw.models.Subreddit, num_posts: int, time_filter: str = "day") -> List[praw.models.Submission]:
    """
    Retrieve a specified number of top posts from a subreddit.
    Args:
        sub (praw.models.Subreddit): Subreddit instances.
        num_posts (int): The number of top posts to retrieve from the subreddit.
        time_filter (str, optional): The time period to filter posts by. Default is "day".
            Possible values: "all", "day", "hour", "month", "week", "year".
    Returns:
        List[praw.models.Submission]: List of top posts for the respective subreddit.
    """
    posts = []
    try:
        for submission in sub.top(limit = num_posts, time_filter = time_filter):
            posts.append(submission)
    except Exception as e:
        print(f"Error processing posts from subreddit {sub.display_name} : Exception: ")

    return posts

def probe_posts_for_comments(submission: praw.models.Submission, num_comments: int, sort_type: str, replace_more_limit: int | None) -> List[praw.models.Comment]:
    """
    Retrieve comments from a Reddit submission and return a list of comments.
    Args:
        submission (praw.models.Submission): The Reddit submission object.
        num_comments (int): The number of comments to retrieve.
        sort_type (str): The sorting type for comments.
            Possible values: 'confidence', 'top', 'new', 'controversial', 'old', 'random', 'qa'.
    Returns:
        List[praw.models.Comment]: A list of comment objects retrieved from the submission.
    """
    comments_list = []
    submission.comment_sort = sort_type
    submission.comment_limit = num_comments

    submission.comments.replace_more(limit=replace_more_limit)
    for comment in submission.comments.list():
        if isinstance(comment, praw.models.MoreComments):
            continue
        comments_list.append(comment)
    return comments_list

def create_post_link(permalink: str) -> str:
    link = "https://www.reddit.com" + permalink
    return link

def create_comment_link(post_permalink: str, comment_id: str) -> str:
    link = "https://www.reddit.com" + post_permalink + comment_id + "/"
    return link