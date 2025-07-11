from nltk.tokenize import word_tokenize
import nltk
import sentiment140
import pandas as pd
import os
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from tqdm import tqdm

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression


results_dict = {}

df = pd.read_csv(os.path.join(sentiment140.download_to, sentiment140.sentiment140_embeddings), encoding='utf-8')
df.dropna(inplace=True)

embedding_dict={}
with open('datasets/GloVe/glove.twitter.27B.50d.txt','r') as f:
    for line in f:
        values = line.split()
        word = values[0]
        vectors = np.asarray(values[1:], 'float32')
        embedding_dict[word] = vectors
f.close()

tokenizer_obj = Tokenizer()
tokenizer_obj.fit_on_texts(df['clean_text'])
sequences = tokenizer_obj.texts_to_sequences(df['clean_text'])

# padded = pad_sequences(sequences, padding='post')

# word_index = tokenizer_obj.word_index

# num_words = len(word_index)+1
# embedding_matrix = np.zeros((num_words, 50))

# for word,i in tqdm(word_index.items()):
#     if i > num_words:
#         continue
    
#     emb_vec=embedding_dict.get(word)
#     if emb_vec is not None:
#         embedding_matrix[i] = emb_vec