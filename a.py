
import asyncpraw
import asyncio
import csv
import matplotlib.pyplot as plt
import requests
import asyncprawcore
import time
import os
import pandas as pd
import numpy as np
import gradio as gr

from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
from asyncpraw.models import MoreComments, Submission
from tqdm import tqdm
from huggingface_hub import InferenceClient, notebook_login
from datetime import datetime, timedelta
from datasets import load_dataset
from helper import get_access_to_reddit, get_write_access_to_hf, search_subreddits_by_keyword_in_name_or_description, filter_subreddits_by_keywords, get_subreddits_name_title_description, process_output, probe_subs_for_posts, default_dict_dict_dict_list, probe_submissions_for_comments, results_str_to_dict

async def main_async():
  results = {}
  reddit = get_access_to_reddit()

  # -- read in files --
  print("reading in files...")

  # read in subreddits csv and convert the display names column to a set
  subreddits_csv_df = pd.read_csv("subreddits_passed_topic_classifier.csv")
  subreddits_display_names_set = set(subreddits_csv_df["Display Name"])

  # read in csvs that store subsidiaries and keywords for each parent company
  subsidiaries_csv_df = pd.read_csv("subsidiary_parent.csv")
  subsidiary_parent_dict = defaultdict(list)
  for subsidiary, parent in zip(subsidiaries_csv_df["Subsidiary"], subsidiaries_csv_df["Parent Company"]):
    subsidiary_parent_dict[parent].append(subsidiary)

  keywords_csv_df = pd.read_csv("parent_keywords.csv")
  parent_keywords_dict = dict(zip(keywords_csv_df["Parent Company"], keywords_csv_df["Keywords"]))

  # -- extract subreddits using keywords technique --
  print("extracting subreddits using keywords technique...")

  # company is the key and associated subreddits as a list of subreddit objects
  subreddits_to_include = {}
  # count how many subreddits were originally extracted
  all_sub_count = 0
  # for each index, company name of the seven companies
  for parent, subsidiaries in subsidiary_parent_dict.items():
    for subsidiary in subsidiaries:
      # get all the subreddits that have that company name in the title or description
      all_subreddits_for_company = await search_subreddits_by_keyword_in_name_or_description(reddit, subsidiary)
      # increment total subreddit count by how many subreddits were extracted
      all_sub_count += len(all_subreddits_for_company)
      # further filter these subreddits based on how many keywords associated with the current company they contain
      filtered_subreddits = await filter_subreddits_by_keywords(subreddits=all_subreddits_for_company,
                                                                keywords=parent_keywords_dict[parent],
                                                                min_keyword_count=1)
      # store filtered subsidiary/parent company subreddits at appropriate key
      subreddits_to_include[parent] = filtered_subreddits

  results["Num subreddits with subsidiary/parent company name in its name or description"] = all_sub_count
  results["Num subreddits after using keywords filter"] = sum([len(company_subreddits) for company_subreddits in subreddits_to_include.values()])

  # -- pass new subreddits through classifier to determine if they are technology related --
  print("passing new subreddits through classifier to determine if they are technology related...")

  topic_classifier_client = InferenceClient(model="gulnuravci/subreddit_description_topic_classifier", token=os.getenv("REDDIT_READ"))

  # key is the parent company and the value is a list of subreddit objects that are technology related
  subreddits_passed_topic_classifier = defaultdict(list)
  # count new subreddits
  num_companies_through_model = 0
  # for each company key in the subreddits to include (based on keyword filtering) dictionary
  for company, subreddits_list in tqdm(subreddits_to_include.items()):
    # get a dictionary where the key is the subreddit object and value is text format of the company's name, title, and description
    name_title_descriptions = get_subreddits_name_title_description(subreddits_to_include[company])
    # for each subreddit under the current company
    for subreddit_object, subreddit_description in name_title_descriptions.items():
      # if subreddit is not new, skip inference
      if subreddit_object.display_name in subreddits_display_names_set:
        subreddits_passed_topic_classifier[company].append(subreddit_object)
        continue

      # pass the subreddit's description through the subreddit topic classifier
      output = topic_classifier_client.text_classification(subreddit_description)

      # process output
      output = process_output(output)

      # if technology related
      if output['TECHNOLOGY RELATED'] > output['NOT TECHNOLOGY RELATED']:
        subreddits_passed_topic_classifier[company].append(subreddit_object)

      num_companies_through_model += 1
    # time.sleep(10)
  parent_company_counts = {parent_company: len(subreddits) for parent_company, subreddits in subreddits_passed_topic_classifier.items()}

  results["Num old subreddits that were automatically included"] = len(subreddits_display_names_set)
  results["Num subreddits that ran through the model"] = num_companies_through_model
  results["Total subreddits that are technology related (including old and new subreddits)"] = sum([len(items) for items in subreddits_passed_topic_classifier.values()])
  results["Num subreddits that were included per parent company"] = parent_company_counts

  # -- get posts from subreddits --
  print("getting posts from subreddits...")

  parent_company_posts = {}
  parent_company_post_counts = {}
  failed_subreddits = defaultdict(list)
  for parent_company, subreddits in tqdm(subreddits_passed_topic_classifier.items()):
    # get X amount of posts from each of the subreddits associated with the current parent company
    current_parent_company_posts, current_failed_subreddits = await probe_subs_for_posts(subreddits, num_posts=2)
    # store failed subreddits
    failed_subreddits[parent_company].extend(current_failed_subreddits)
    # add key -> parent company, value -> dictionary where key is subreddit object and value is list of submission objects
    parent_company_posts[parent_company] = current_parent_company_posts
    # count how many posts are added per parent company
    parent_company_post_counts[parent_company] = sum(len(value) for key, value in current_parent_company_posts.items())
    # time.sleep(20)

  results["Num of posts extracted for each parent company"] = parent_company_post_counts
  results["Failed subreddits while extracting posts"] = failed_subreddits

  # -- get comments from posts --
  print("getting comments from posts...")

  post_comments = default_dict_dict_dict_list()
  post_comment_counts = defaultdict(int)
  for parent_company, subreddit_dict in tqdm(parent_company_posts.items()):
    for subreddit, posts in subreddit_dict.items():
      for post in posts:
        # get X relevant comments
        comments = await probe_submissions_for_comments(submission = post,
                                                  num_comments = 2,
                                                  sort_type = "best")
        post_comments[parent_company][subreddit][post] = comments
        post_comment_counts[parent_company] += len(comments)
    #     time.sleep(1)
      time.sleep(5)
    # time.sleep(20)

  results["Num of comments extracted for each parent company"] = post_comment_counts
  post_comments_save = post_comments
  return results, post_comments

def main(results, post_comments):
  # -- run posts and comments through sentiment analysis --
  print("running posts and comments through sentiment analysis...")

  API_URL = "https://wk6x4kfrdikhsi0n.us-east-1.aws.endpoints.huggingface.cloud"
  headers = {
    "Accept" : "application/json",
    "Authorization": "Bearer " + os.getenv("REDDIT_READ"),
    "Content-Type": "application/json"
  }

  def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

  query({
      "inputs": "testing economy is great",
      "parameters": {}
  })
  time.sleep(20)
    
  query({
      "inputs": "testing economy sucks",
      "parameters": {}
  })
  time.sleep(20)

  sentiments = {"Apple":[], "Microsoft":[], "Alphabet":[], "Amazon":[], "Nvidia":[], "Tesla":[], "Meta":[]}
  interactions = {"Apple":0, "Microsoft":0, "Alphabet":0, "Amazon":0, "Nvidia":0, "Tesla":0, "Meta":0}
  neutral_sentiments = {"Apple":0, "Microsoft":0, "Alphabet":0, "Amazon":0, "Nvidia":0, "Tesla":0, "Meta":0}
  positive_sentiments = {"Apple":0, "Microsoft":0, "Alphabet":0, "Amazon":0, "Nvidia":0, "Tesla":0, "Meta":0}
  negative_sentiments = {"Apple":0, "Microsoft":0, "Alphabet":0, "Amazon":0, "Nvidia":0, "Tesla":0, "Meta":0}

  for parent_company, subreddit_dict in tqdm(post_comments.items()):
    for subreddit, posts in subreddit_dict.items():
      for post, comments in posts.items():
        total_interaction = 0
        sentiment_weights = 0
        post_text = post.title + post.selftext

        post_sentiment = query(
        {
          "inputs": post_text[:512],
          "parameters": {}
        })

        if not post_sentiment: continue

        # if the highest score is neutral
        if post_sentiment[0]['label'] == 'neutral':
          post_sentiment = 0
          neutral_sentiments[parent_company] += 1
        # if the highest score is positive
        elif post_sentiment[0]['label'] == 'positive':
          post_sentiment = post_sentiment[0]['score']
          positive_sentiments[parent_company] += 1
        # if the highest score is negative
        elif post_sentiment[0]['label'] == 'negative':
          post_sentiment = -post_sentiment[0]['score']
          negative_sentiments[parent_company] += 1

        post_upvote_ratio = post.upvote_ratio

        total_interaction += post_upvote_ratio

        sentiment_weights += post_upvote_ratio * post_sentiment

        for comment in comments:
          comment_sentiment = query(
          {
            "inputs": comment.body[:512],
            "parameters": {}
          })
          # print("post sentiment:", post_sentiment)
          if not comment_sentiment: continue

          # if comment score is neutral
          if comment_sentiment[0]['label'] == 'neutral':
            comment_sentiment = 0
            neutral_sentiments[parent_company] += 1
          # if comment score is positive
          elif comment_sentiment[0]['label'] == 'positive':
            comment_sentiment = comment_sentiment[0]['score']
            positive_sentiments[parent_company] += 1
          # if comment score is negative
          elif comment_sentiment[0]['label'] == 'negative':
            comment_sentiment = -comment_sentiment[0]['score']
            negative_sentiments[parent_company] += 1

          comment_score = comment.score

          total_interaction += comment_score
          sentiment_weights += comment_score * comment_sentiment

        if total_interaction:
          total_sentiment = sentiment_weights/total_interaction
        else:
          total_sentiment = 0
        sentiments[parent_company].append(total_sentiment)
        interactions[parent_company] += total_interaction

  results["Num of interactions for each parent company"] = interactions
  results["Num of neutral sentiments for each parent company"] = neutral_sentiments
  results["Num of positive sentiments for each parent company"] = positive_sentiments
  results["Num of negative sentiments for each parent company"] = negative_sentiments

  # -- calculate average sentiments --
  print("calculating average sentiments...")
  average_sentiments = {}
  for parent_company, sentiment_values in sentiments.items():
    average_sentiments[parent_company] = sum(sentiment_values)/len(sentiment_values)

  average_sentiments

  results["Average sentiment for each parent company"] = average_sentiments

  print("returning results...")
  return results

def plot_results(results):
  color_map = {
      'Apple': 'lightgray',
      'Microsoft': 'deepskyblue',
      'Alphabet': 'yellow',
      'Amazon': 'orange',
      'Nvidia': 'limegreen',
      'Tesla': 'red',
      'Meta': 'royalblue'
  }
  fig, axs = plt.subplots(figsize=(8, 6))
  for company, num_subs in results["Num subreddits that were included per parent company"].items():
    plt.barh(company, num_subs, color=color_map.get(company, 'gray'))
  axs.set_title('Number of Subreddits per Parent Company')
  axs.set_xlabel('Number of Technology Related Subreddits')
  plt.tight_layout()
  plt.savefig("results_num_subs.png")

  fig, axs = plt.subplots(figsize=(8, 6))
  for company, num_posts in results["Num of posts extracted for each parent company"].items():
    axs.barh(company, num_posts, color=color_map.get(company, 'gray'))
  axs.set_title('Number of Posts Extracted per Parent Company')
  axs.set_xlabel('Number of Posts')
  plt.tight_layout()
  plt.savefig("results_num_posts.png")

  fig, axs = plt.subplots(figsize=(8, 6))
  for company, num_comments in results["Num of comments extracted for each parent company"].items():
    axs.barh(company, num_comments, color=color_map.get(company, 'gray'))
  axs.set_title('Number of Comments Extracted per Parent Company')
  axs.set_xlabel('Number of Comments')
  plt.tight_layout()
  plt.savefig("results_num_comments.png")

  fig, axs = plt.subplots(figsize=(8, 6))
  for company, num_interactions in results["Num of interactions for each parent company"].items():
    axs.barh(company, num_interactions, color=color_map.get(company, 'gray'))
  axs.set_title('Number of Interactions per Parent Company')
  axs.set_xlabel('Number of Interactions')
  plt.tight_layout()
  plt.savefig("results_num_interactions.png")

  fig, axs = plt.subplots(figsize=(8, 6))
  for company, num_interactions in results["Average sentiment for each parent company"].items():
    axs.barh(company, num_interactions, color=color_map.get(company, 'gray'))
  axs.set_title('Average Sentiment per Parent Company')
  axs.set_xlabel('Average Sentiment')
  axs.set_xlim(-1, 1)  # Set the x-axis limits to range from -1 to 1
  plt.tight_layout()
  plt.savefig("results_average_sentiment.png")

  fig, axs = plt.subplots(figsize=(8, 6))
  bar_width = 0.25
  index = np.arange(7)

  companies = list(results["Num of positive sentiments for each parent company"].keys())
  positive_sentiments = [results["Num of positive sentiments for each parent company"][company] for company in companies]
  negative_sentiments = [results["Num of negative sentiments for each parent company"][company] for company in companies]
  neutral_sentiments = [results["Num of neutral sentiments for each parent company"][company] for company in companies]

  axs.bar(index, positive_sentiments, bar_width, label='Positive Sentiments', color='skyblue')
  axs.bar(index + bar_width, negative_sentiments, bar_width, label='Negative Sentiments', color='salmon')
  axs.bar(index + 2 * bar_width, neutral_sentiments, bar_width, label='Neutral Sentiments', color='lightgreen')

  axs.set_ylabel('Number of Sentiments')
  axs.set_title('Sentiment Distribution for Each Parent Company')
  axs.set_xticks(index + bar_width)
  axs.set_xticklabels(companies, rotation=45)
  axs.legend()
  plt.tight_layout()
  plt.savefig("results_sentiment_distribution.png")

def plot():
    # load results dataset from hugging face
    reddit_sentiment_analysis_results = load_dataset("gulnuravci/reddit_sentiment_analysis_results", split="train")
    
    # return latest results
    latest_results = reddit_sentiment_analysis_results[-1]
    
    # convert string datetime to datetime object
    latest_results_datetime = datetime.strptime(reddit_sentiment_analysis_results[-1]['Datetime'], "%Y-%m-%d %H:%M:%S")
    
    # get current time
    current_datetime = datetime.now()
    
    # calculate the time difference between the current datetime and the datetime of the last entry
    time_difference = current_datetime - latest_results_datetime
    
    print("time_difference > timedelta(hours=24):", time_difference > timedelta(hours=24))
        
    # check if the time difference is greater than 24 hours
    if time_difference < timedelta(hours=24):
        results = results_str_to_dict(latest_results)
    else:
        # define an asynchronous function to fetch today's results
        async def fetch_todays_results():
            async_results, post_comments = await main_async()
            return main(async_results, post_comments)
        # run the asynchronous function and wait for the results
        todays_results = asyncio.run(fetch_todays_results())
        # add datetime to results
        todays_results["Datetime"] = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # convert non string values to string
        todays_results = {key: str(value) for key, value in todays_results.items()}
        # add results to dataset
        reddit_sentiment_analysis_results = reddit_sentiment_analysis_results.add_item(todays_results)
        # get write permission to hugging face
        get_write_access_to_hf()
        # push to hugging face
        reddit_sentiment_analysis_results.push_to_hub("gulnuravci/reddit_sentiment_analysis_results")
        # convert string results to dict
        results = results_str_to_dict(todays_results)
    
    plot_results(results)
    return "results_num_subs.png", "results_num_posts.png", "results_num_comments.png", "results_num_interactions.png", "results_average_sentiment.png", "results_sentiment_distribution.png"

def launch_gradio_app():
  title = "Reddit Sentiment Analysis🎭📈⌨️"
  description = "I built a tool that extracts daily content using the Reddit API to calculate sentiment scores about the Reddit community's views on leading tech companies such as Apple, Microsoft, Alphabet, Amazon, Nvidia, Tesla, Meta."
  article = "I also built a cool website to explain the project, so click [here](https://gulnuravci.github.io/scripts/project_pages/reddit_sentiment_analysis/reddit_sentiment_analysis.html) to learn more."

  demo = gr.Interface(plot,
                      inputs=None,
                      outputs=[gr.Gallery(label="Today", show_label=False, elem_id="gallery", columns=[2], rows=[3], object_fit="contain", height="auto")],
                      title=title,
                      description=description,
                      article=article)
    
  demo.launch()

launch_gradio_app()