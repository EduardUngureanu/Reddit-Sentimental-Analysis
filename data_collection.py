import json
import pandas as pd
import praw
import reddit_helper
import database_helper
from datetime import datetime
import os
import sqlite3
import data_processing

def create_reddit_db_folder() -> str:
    """
    Will create a new folder with the path `./reddit_data/<creation datetime>` datetime being formatted as `%Y-%m-%d_%H-%M-%S`

    Returns:
        str : Path to the folder.

    """
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_folder = f"./reddit_data/{current_datetime}"

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    return new_folder

def collect_dedicated(reddit_con: praw.Reddit, reddit_db_cur: sqlite3.Cursor):
    """
    Collect data from dedicated community subreddits, as in the subreddits listed in the `companies.json` file.

    Args:
        reddit_con (praw.Reddit) : Reddit connection instance.
        reddit_db_cur (sqlite3.Cursor) : SQLite cursor to the a reddit database.

    """
    with open("companies.json", "r") as fd:
        companies = json.load(fd)
        print(f"\n\n############# Probing DEDICATED subreddits #############")
        for company in companies:
            company_name = company["name"]
            print(f"Probing subreddits for {company_name}")
            sub_name_list = company["subs"]
            # Form the subreddit list for each company
            sub_list = [reddit_con.subreddit(sub_name) for sub_name in sub_name_list]
            company_post_count = 0
            company_comment_count = 0
            for sub in sub_list:
                # Getting the subreddit display_name instead of using the file data as the data might not be formatted correctly
                sub_display_name = sub.display_name
                print(f" - Probing {sub_display_name} for posts")
                posts = reddit_helper.probe_sub_for_top_posts(sub, 20)
                sub_post_count = 0
                sub_comment_count = 0
                for post in posts:
                    post_comment_count = 0
                    comments = reddit_helper.probe_posts_for_comments(post, 50, 'best', 2)

                    # Getting early, needed for comments
                    post_id = post.id
                    post_permalink = post.permalink

                    # is_self tells you if its a selfpost (text and stuff) or a link post (media or link)
                    # Post body is either the text of the post or the URL if its a link post (media or link)
                    if (is_self := post.is_self):
                        post_body = post.selftext
                    else:
                        post_body = post.url
                    
                    database_helper.insert_into_posts(reddit_db_cur,
                                                      company_name,
                                                      sub_display_name,
                                                      post_id,
                                                      post.title,
                                                      post_body,
                                                      is_self,
                                                      post.created_utc,
                                                      reddit_helper.create_post_link(post_permalink),
                                                      post.upvote_ratio,
                                                      post.score)
                    
                    for comment in comments:
                        comment_id = comment.id
                        # `post_id` is the submission ID but `parent_id` is ID of the parent comment (prefixed with `t1_`) or, if it is a top-level comment, it will be the submission ID again instead (prefixed with `t3_`)
                        database_helper.insert_into_comments(reddit_db_cur,
                                                             company_name,
                                                             sub_display_name,
                                                             post_id, 
                                                             comment.parent_id,
                                                             comment_id,
                                                             comment.body,
                                                             comment.created_utc,
                                                             reddit_helper.create_comment_link(post_permalink, comment_id),
                                                             comment.score)
                        post_comment_count += 1
                    
                    print(f" - - Added {post_comment_count} comments from post {post_id}")
                    sub_post_count += 1
                    sub_comment_count += post_comment_count
                
                print(f" - {sub_display_name} TOTALS : {sub_post_count} posts | {sub_comment_count} comments")
                company_post_count += sub_post_count
                company_comment_count += sub_comment_count

            print(f"{company_name} company TOTALS : {company_post_count} posts | {company_comment_count} comments")
                        
# Mostly a repeat of collect_dedicated with the company stuff removed, company just set to None, will be assigned later
def collect_generic(reddit_con: praw.Reddit, reddit_db_cur: sqlite3.Cursor):
    """
    Collect data from broader subreddits, as in the subreddits listed in the `generic.json` file. The `company` field in the tables will be empty when initially created.

    Args:
        reddit_con (praw.Reddit) : Reddit connection instance.
        reddit_db_cur (sqlite3.Cursor) : SQLite cursor to the a reddit database.

    """
    with open("generic.json", "r") as fd:
        print(f"\n\n############# Probing GENERIC subreddits #############")
        sub_name_list = json.load(fd)

        sub_list = [reddit_con.subreddit(sub_name) for sub_name in sub_name_list]

        company_name = None
        for sub in sub_list:
            # Getting the subreddit display_name instead of using the file data as the data might not be formatted correctly
            sub_display_name = sub.display_name
            print(f" - Probing {sub_display_name} for posts")
            posts = reddit_helper.probe_sub_for_top_posts(sub, 20)
            sub_post_count = 0
            sub_comment_count = 0
            for post in posts:
                post_comment_count = 0
                comments = reddit_helper.probe_posts_for_comments(post, 100, 'best', 2)

                # Getting early, needed for comments
                post_id = post.id
                post_permalink = post.permalink

                # is_self tells you if its a selfpost (text and stuff) or a link post (media or link)
                # Post body is either the text of the post or the URL if its a link post (media or link)
                if (is_self := post.is_self):
                    post_body = post.selftext
                else:
                    post_body = post.url
                
                database_helper.insert_into_posts(reddit_db_cur,
                                                    company_name,
                                                    sub_display_name,
                                                    post_id,
                                                    post.title,
                                                    post_body,
                                                    is_self,
                                                    post.created_utc,
                                                    reddit_helper.create_post_link(post_permalink),
                                                    post.upvote_ratio,
                                                    post.score)
                
                for comment in comments:
                    comment_id = comment.id
                    # `post_id` is the submission ID but `parent_id` is ID of the parent comment (prefixed with `t1_`) or, if it is a top-level comment, it will be the submission ID again instead (prefixed with `t3_`)
                    database_helper.insert_into_comments(reddit_db_cur,
                                                            company_name,
                                                            sub_display_name,
                                                            post_id, 
                                                            comment.parent_id,
                                                            comment_id,
                                                            comment.body,
                                                            comment.created_utc,
                                                            reddit_helper.create_comment_link(post_permalink, comment_id),
                                                            comment.score)
                    post_comment_count += 1
                
                print(f" - - Added {post_comment_count} comments from post {post_id}")
                sub_post_count += 1
                sub_comment_count += post_comment_count
            
            print(f" - {sub_display_name} TOTALS : {sub_post_count} posts | {sub_comment_count} comments")

def collect():
    reddit_con = reddit_helper.get_access_to_reddit("user.json")

    path = create_reddit_db_folder()

    reddit_db_con = database_helper.get_reddit_db_connection(f"{path}/data.db")
    reddit_db_cur = reddit_db_con.cursor()

    collect_dedicated(reddit_con, reddit_db_cur)
    collect_generic(reddit_con, reddit_db_cur)

    data_processing.process_database(reddit_db_con)

    reddit_db_cur.close()
    reddit_db_con.close()

collect()