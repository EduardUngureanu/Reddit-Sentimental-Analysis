from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import GoEmotions
import sentiment140
import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression


GoEmotion_label_map = {
    0: -2,  # Very Negative
    1: -1,  # Negative
    2:  0,  # Neutral
    3:  1,  # Positive
    4:  2   # Very Positive
}

Sentiment140_label_map = {
    0: -1,
    1: 1
}

df_train = pd.read_csv(os.path.join(sentiment140.download_to, sentiment140.sentiment140_lemmatized))
df_train.dropna(inplace=True)

df_train['sentiment'] = df_train['sentiment'].map(Sentiment140_label_map)

x_train = df_train['clean_text']
y_train = df_train['sentiment']

Sentiment140_model = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', LogisticRegression(solver='saga', penalty='l2', max_iter=1000, n_jobs=8))
])

Sentiment140_model.fit(x_train, y_train)
joblib.dump(Sentiment140_model, 'Sentiment140_model.pkl')

df_train = pd.read_csv(os.path.join(GoEmotions.download_to, GoEmotions.train_stemmed), encoding='utf-8')
df_train.dropna(inplace=True)

df_train['label'] = df_train['label'].map(GoEmotion_label_map)

x_train = df_train['clean_text']
y_train = df_train['label']

GoEmotions_model = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', SGDClassifier(loss='log_loss', penalty='l2', max_iter=1000, tol=1e-3, n_jobs=8))
])

GoEmotions_model.fit(x_train, y_train)
joblib.dump(GoEmotions_model, 'GoEmotions_model.pkl')