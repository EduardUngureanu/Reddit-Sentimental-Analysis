from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import sentiment140
import os
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
import pandas as pd
import json

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression

working_directory = "testing\\Sentiment140"

def test_pipeline(x_train, x_test, y_train, y_test, vectorizer, model):
    pipeline = make_pipeline(vectorizer, model)
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)

    return classification_report(y_test, y_pred, digits=4), classification_report(y_test, y_pred, output_dict=True)

def test_sentiment140():
    vectorizers = {"CountVectorizer" : CountVectorizer(),
                "TfidfVectorizer" : TfidfVectorizer()}

    models = {"MultinomialNB": MultinomialNB(alpha=0.1),
              "LinearSVC": LinearSVC(max_iter=10000, dual=False, random_state=42),
              "SGDClassifier": SGDClassifier(loss='log_loss', penalty='l2', max_iter=1000, tol=1e-3, random_state=42, n_jobs=8),
              "LogisticRegression": LogisticRegression(solver='saga', penalty='l2', max_iter=1000, random_state=42, n_jobs=8)}


    # models = {"MultinomialNB" : MultinomialNB(),
    #         "LinearSVC" : LinearSVC(),
    #         "SGDClassifier" : SGDClassifier(),
    #         "LogisticRegression" : LogisticRegression(solver='liblinear', max_iter=1000)}

    results_dict = {}
    with open(os.path.join(working_directory, "sklearn_results_sentiment140.txt"), "w") as f:
        df = pd.read_csv(os.path.join(sentiment140.download_to, "sentiment140_processed_stemmed.csv"), encoding='utf-8')
        df.dropna(inplace=True)
        type = "Stemmed"
        results_dict[type] = {}
        x_train, x_test, y_train, y_test = train_test_split(df['clean_text'], df['sentiment'], test_size=0.25, random_state=1337)
        for vec_name, vec in vectorizers.items():
            results_dict[type][vec_name] = {}
            for model_name, model in models.items():
                output = f"{type} | {vec_name} | {model_name}"
                print(output)
                f.write(f"{output}\n")
                report, report_dict = test_pipeline(x_train, x_test, y_train, y_test, vec, model)
                print(report)
                f.write(f"{report}\n")
                results_dict[type][vec_name][model_name] = report_dict

        df = pd.read_csv(os.path.join(sentiment140.download_to, "sentiment140_processed_lemmatized.csv"), encoding='utf-8')
        df.dropna(inplace=True)
        type = "Lemmatized"
        results_dict[type] = {}
        x_train, x_test, y_train, y_test = train_test_split(df['clean_text'], df['sentiment'], test_size=0.25, random_state=1337)
        for vec_name, vec in vectorizers.items():
            results_dict[type][vec_name] = {}
            for model_name, model in models.items():
                output = f"{type} | {vec_name} | {model_name}"
                print(output)
                f.write(f"{output}\n")
                report, report_dict = test_pipeline(x_train, x_test, y_train, y_test, vec, model)
                print(report)
                f.write(f"{report}\n")
                results_dict[type][vec_name][model_name] = report_dict

    with open(os.path.join(working_directory,"sklearn_results_sentiment140.json"), "w") as f:
        json.dump(results_dict, f)

test_sentiment140()