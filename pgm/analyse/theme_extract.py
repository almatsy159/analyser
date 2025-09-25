import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re
import spacy 
import joblib

# not clean path ! should use pathlib (probably ?)
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)   # supprimer URLs
    text = re.sub(r"@\w+", "", text)             # supprimer mentions
    text = re.sub(r"#\w+", "", text)             # supprimer hashtags
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", "", text)  # caractères spéciaux
    return text.strip()

def lemmatyse(nlp,stopwords,text):

    doc = nlp(text)
    lemmas = [
        tok.lemma_
        for tok in doc
        if tok.is_alpha and tok.lemma_ not in stopwords
    ]

    return " ".join(lemmas)

#clean_texts = [clean_text(t) for t in texts[:5000]]  # échantillon de 5000 tweets

"""

"""

dir_data = "/home/alma/analyser/data/"
#file = "french_tweets.csv"
file = "ds_from_txt.jsonl"
stop_word_to_add = {"jai",'aa','aaaah','aaaah','oeuf'}

# this function is not called yet seem to be clean + lemmatyse 
"""
def preprocess(texts):
    stopwords = nlp.Defaults.stop_words.union({"rt", "mdr", "ptdr", "jai", "jsuis"})
    clean = []
    for t in texts:
        doc = nlp(t)
        lemmas = [tok.lemma_.lower() for tok in doc if tok.is_alpha and tok.lemma_.lower() not in stopwords]
        clean.append(" ".join(lemmas))
    return clean
"""
def get_file_extension(filename):
    """
    Returns the file extension of a given filename.
    If there is no extension, returns None.
    """
    match = re.search(r"\.([^.]+)$", filename)
    if match:
        return match.group(1)
    return None

def get_filename_without_extension(filename):
    """
    Returns the filename without its extension.
    If there is no extension, returns the original filename.
    """
    match = re.match(r"^(.*?)(\.[^.]+)?$", filename)
    if match:
        return match.group(1)
    return filename


def preprocess(text):
    nlp = spacy.load("fr_core_news_sm")
    french_stopwords = nlp.Defaults.stop_words
    french_stopwords = french_stopwords.union(stop_word_to_add)
    french = [w for w in french_stopwords]


    clean_texts = lemmatyse(nlp,french,clean_text(text))

    return clean_texts

def train_lda(file,f_dir=dir_data,nb_topics=50,nb_states=50,max_df=0.95,min_df=3,rows_df=100,to_print=True):

    file_ext = get_file_extension(file)
    f_path = f_dir + "datasets/" + file
    
    # load data into with panda from given dir/file path (may handle more cases)
    df = None
    if file_ext != None:
        match file_ext :
            case "csv":
                df = pd.read_csv(f_path)
            case "json":
                df = pd.read_json(f_path)
            case "jsonl":
                df = pd.read_json(f_path)
            case _ :
                raise TypeError
    
  

    # load french stopword and put them in an array to vectorise it
    #nlp = spacy.load("fr_core_news_sm")
    #print("nlp :",nlp.Defaults.stop_words)
    #french_stopwords = nlp.Defaults.stop_words
    #french_stopwords = french_stopwords.union(stop_word_to_add)
    french_stopwords = stop_word_to_add
    print(french_stopwords)
    french = [w for w in french_stopwords]

    # clean data
    """
    texts = df["text"].dropna().astype(str).tolist()
    #clean_texts = [lemmatyse(nlp,french,clean_text(t)) for t in texts[0:rows_df]] 
    clean_texts = [clean_text(t) for t in texts[0:rows_df]] 
    print("clean text :",clean_texts)
    """
    texts = df["text"]
    print("df : ",texts[0:rows_df])
    clean_texts = [preprocess(t) for t in texts[0:rows_df]]
    print("clean text :",clean_texts)

    vectorizer = CountVectorizer(max_df=max_df, min_df=min_df, stop_words=french)

    # put occurence in a matrix M:(nb_docs,nb_words) where M(i,j) = nb_of_occurence_of_word_j in doc_i
    #  dtm = document-term matrix 
    dtm = vectorizer.fit_transform(clean_texts)

    # latent derichlet allocation : algo to uncover topics out of documents
    
    lda = LatentDirichletAllocation(n_components=nb_topics, random_state=nb_states)
    lda.fit(dtm)

    if to_print:
        terms = vectorizer.get_feature_names_out()
        for i, topic in enumerate(lda.components_):
            top_terms = [terms[j] for j in topic.argsort()[-10:]]
            print(f"Thème {i}:", top_terms)

    # Sauvegarde

    f_name = get_filename_without_extension(file)
    model_path = f_dir + "/models/" + f_name
    vectorizer_path = model_path + "_vectoriser.pkl"
    lda_path = model_path + "_lda_model.pkl"
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(lda, lda_path)

    print("✅ Modèle sauvegardé")
    
    
    #return vectorizer_path,lda_path

def predict_theme(text,file,f_dir=dir_data,n_top_words=10):
    f_name = get_filename_without_extension(file)
    model_path = f_dir + "/models/" + f_name
    vectorizer_path = model_path + "_vectoriser.pkl"
    lda_path = model_path + "_lda_model.pkl"
    
    # Charge model ou entraine puis charge si inexistant

    try :
        vectorizer = joblib.load(vectorizer_path)
        lda = joblib.load(lda_path)
        print("exist !")

    except :
        print("don't exist => train model")
        train_lda(file,f_dir)
        print("trained")
        vectorizer = joblib.load(vectorizer_path)
        lda = joblib.load(lda_path)
    


    # Nettoyage + vectorisation
    clean_text = preprocess(text)
    print("clean text :",clean_text)
    dtm_new = vectorizer.transform([clean_text])

    # Distribution thématique
    dist = lda.transform(dtm_new)[0]
    dominant_topic = dist.argmax()

    """
    terms = vectorizer.get_feature_names_out()
    for i, topic in enumerate(lda.components_):
        top_terms = [terms[j] for j in topic.argsort()[-10:]]
        print(f"Thème {i}:", top_terms)
    """
    print("Distribution thématique :", dist)
    print("Thème dominant :", dominant_topic)

    terms = vectorizer.get_feature_names_out()
    print("terms : ",terms)
    topics = {}
    for idx,topic in enumerate(lda.components_):
        top_features = topic.argsort()[: -n_top_words - 1:-1]
        topics[idx] = [terms[i] for i in top_features]
    print("topics : ",topics)
    dominant_words = topics[dominant_topic]
    print("dominant words : ",dominant_words)
    #return dominant_topic, dist

if __name__ == "__main__":

    text = """fait n°1: toute IA t'explose en SQL
fait n°2: SQL est un langage clé en data. 
Alors, faut il pratiquer ?

la réponse sans suspense: oui

quelques infos sur SQL avant de te dire comment

SQL se dit "cikouelle" dans les salons feutrés des sachants et pas "esse-ku-aile"

SQL c'est LE language de requête de base de donnée jamais remplacé depuis des dizaines d'années

SQL c'est aussi l'unique occasion de se servir des majuscules de son clavier AZERTY. Quel bonheur

et surtout en data, il y a de grandes chances qu'on te propose un petit test technique en SQL pour 2e entretien

alors, comment pratiquer ?

oui, comment pratiquer SQL gratuitement ?

un site: sql-practice . com

3 niveaux de difficulté

2 bases exemples

des indices pour répondre

le tout, gratuitement dans ton navigateur

(ce post n'est pas sponsorisé, j'utilise juste ce site de temps en temps pour me rafraîchir entre 2 prompts)

Septembre est une période propice pour rafraîchir ses automatismes en data,
et sinon, n'oublie pas de mentionner SQL dans ton CV de data expert

bons exos!"""
    #predict_theme(text,file,dir_data)
    text2 = """"Certains traits associés à l’impulsivité et au manque d’empathie pourraient paradoxalement favoriser leur succès sexuel sur l’application."...🤔

👉En France environ 1 couple sur 5 formé en ligne actuellement.

Ces applications de rencontre comme Tinder changent la façon dont les humains se reproduisent et pas forcément en bien...

🔹️Le Problème

Tinder fonctionne un peu comme un jeu vidéo : swipe rapide, photos attirantes, conversations courtes. 

Ce système #favorise les hommes qui savent #mentir et #manipuler, parce qu'ils sont doués pour créer de faux profils séduisants et dire ce que les femmes veulent entendre.

L'étude menée par Dr. Lennart Freyth (Université Johannes Kepler) et #PeterJonason (Université Cardinal Stefan) publiée dans Cyberpsychology, Behavior, and Social Networking. montre que les hommes avec des traits de "#psychopathe" (égoïstes, menteurs, sans empathie) ont plus de #succès #sexuel sur ces apps que dans la vraie vie.

Ils utilisent l'application comme un outil pour trouver plus facilement des femmes qu'ils arrivent à manipuler pour assouvir un besoin sexuel ou former un couple.

🔹️L'Impact 

Les femmes passent selon l'étude beaucoup de temps à choisir des profils et discuter en ligne. 

Quand elles rencontrent finalement le partenaire potentiel, elles se disent "j'ai déjà investi tant d'énergie" et acceptent des choses qu'elles refuseraient normalement.

C'est comme acheter quelque chose de cher qu'on ne veut plus vraiment, mais qu'on garde parce qu'on l'a payé.

🔹️Les Conséquences à long terme ?

👉Si les hommes manipulateurs ont plus d'enfants grâce à ces apps, leurs fils hériteront peut-être de ces traits ?

Les filles grandiront peut-être en pensant que c'est normal d'avoir ce type de relations.

Cela participe à une sélection évolutive par auto-domestication de certaines populations Homo Sapiens via nos #prothèsescognitives...

En gros, ces applications sélectionnent souvent artificiellement les "mauvais" traits humains, or cela mène à des opportunités réelles de reproduction sexuelle... 

un peu comme si on élevait des chiens en ne favorisant que les plus agressifs à se reproduire...

Sauf qu'ici, c'est nous qui nous sélectionnont nous-mêmes sans nous en rendre compte. 

C'est comme si la technologie nous aidait à nous transformer collectivement en une version moins sympathique de l'humanité. 

Dommage.

#réseausociaux #société_ruche"""
predict_theme(text2,file,dir_data)

    
        
