from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import GoEmotions
import os
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
import joblib
from sklearn.pipeline import make_pipeline
import pandas as pd
import json

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression

working_directory = "testing\\GoEmotions"

label_map = {
    0: -2,  # Very Negative
    1: -1,  # Negative
    2:  0,  # Neutral
    3:  1,  # Positive
    4:  2   # Very Positive
}

def test_pipeline(x_train, x_test, y_train, y_test, vectorizer, model):
    pipeline = make_pipeline(vectorizer, model)
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)

    return classification_report(y_test, y_pred, digits=4), classification_report(y_test, y_pred, output_dict=True)

def test_GoEmotions():
    vectorizers = {"CountVectorizer" : CountVectorizer(),
                "TfidfVectorizer" : TfidfVectorizer()}

    models = {"MultinomialNB" : MultinomialNB(),
            "LinearSVC" : LinearSVC(),
            "SGDClassifier" : SGDClassifier(),
            "LogisticRegression" : LogisticRegression(solver='liblinear', max_iter=1000)}

    results_dict = {}

    with open(os.path.join(working_directory, "sklearn_results_GoEmotions_5sentiment.txt"), "w") as f:
        df_train = pd.read_csv(os.path.join(GoEmotions.download_to, GoEmotions.train_stemmed), encoding='utf-8')
        df_test = pd.read_csv(os.path.join(GoEmotions.download_to, GoEmotions.test_stemmed), encoding='utf-8')
        df_train.dropna(inplace=True)
        df_test.dropna(inplace=True)
        # df_train['label'] = df_train['label'].map(label_map)
        # df_test['label'] = df_test['label'].map(label_map)
        type = "Stemmed"
        results_dict[type] = {}
        x_train = df_train['clean_text']
        y_train = df_train['label']
        x_test = df_test['clean_text']
        y_test = df_test['label']
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

        df_train = pd.read_csv(os.path.join(GoEmotions.download_to, GoEmotions.train_lemmatized), encoding='utf-8')
        df_test = pd.read_csv(os.path.join(GoEmotions.download_to, GoEmotions.test_lemmatized), encoding='utf-8')
        df_train.dropna(inplace=True)
        df_test.dropna(inplace=True)
        # df_train['label'] = df_train['label'].map(label_map)
        # df_test['label'] = df_test['label'].map(label_map)
        type = "Lemmatized"
        results_dict[type] = {}
        x_train = df_train['clean_text']
        y_train = df_train['label']
        x_test = df_test['clean_text']
        y_test = df_test['label']
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

    with open(os.path.join(working_directory, "sklearn_results_GoEmotion_5sentiment.json"), "w") as f:
        json.dump(results_dict, f)

test_GoEmotions()