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
import yfinance as yf
import joblib
import database_helper
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import re
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import GoEmotions
import sentiment140
import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
import sqlite3

from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression

# Load model from file
loaded_model = joblib.load('GoEmotions_model.pkl')

# Use the model
print(loaded_model.predict(["this is amazing"]))