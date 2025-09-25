from flask import Flask,request,jsonify
from datasets import load_dataset as ld
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re
import spacy 

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)   # supprimer URLs
    text = re.sub(r"@\w+", "", text)             # supprimer mentions
    text = re.sub(r"#\w+", "", text)             # supprimer hashtags
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", "", text)  # caractères spéciaux
    return text.strip()

#clean_texts = [clean_text(t) for t in texts[:5000]]  # échantillon de 5000 tweets

file = "./data/datasets/french_tweets.csv"

"""
dataset = ld("FrancophonIA/french_tweets",split="train")
#print(dataset[0])

#docs = [x["text"] for x in dataset]
#print(docs[0])

df = pd.DataFrame(dataset)
df.to_json(file)
"""

df = pd.read_csv(file)
print(df.head())

texts = df["text"].dropna().astype(str).tolist()
clean_texts = [clean_text(t) for t in texts[0:500]] 
print(len(clean_texts))
nlp = spacy.load("fr_core_news_sm")
french_stopwords = nlp.Defaults.stop_words
french = [w for w in french_stopwords]
vectorizer = CountVectorizer(max_df=0.99, min_df=4, stop_words=french)
dtm = vectorizer.fit_transform(clean_texts)

#print(df["text"][100])
#print(df.loc[100,"text"])

lda = LatentDirichletAllocation(n_components=5, random_state=5)
lda.fit(dtm)

terms = vectorizer.get_feature_names_out()
for i, topic in enumerate(lda.components_):
    top_terms = [terms[j] for j in topic.argsort()[-10:]]
    print(f"Thème {i}:", top_terms)

app = Flask(__name__)


