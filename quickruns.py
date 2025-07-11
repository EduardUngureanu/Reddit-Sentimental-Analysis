import praw
import json
import praw.models
import reddit_helper
from datetime import datetime
import sqlite3
import database_helper
import pandas as pd
import sentiment140
import GoEmotions
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer

list = ["2025-05-11_16-48-23","2025-05-12_16-46-26", "2025-05-13_16-10-38", "2025-05-14_21-24-24", "2025-05-15_20-56-03", "2025-05-16_18-27-38 dupe", "2025-05-17_20-31-05"]


df = pd.read_csv(os.path.join(GoEmotions.download_to, GoEmotions.train_lemmatized), encoding='utf-8')
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["text"])
print("Vectorized shape:", X.shape)