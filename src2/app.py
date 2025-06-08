from flask import Flask,render_template
import tweepy
import time
import re
from transformers import pipeline
import warnings
import nltk
nltk.download('stopwords')
from pymongo import MongoClient
from nltk.corpus import stopwords
import os

# Connexion MongoDB (adapter l'URL si besoin)
# mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/tweetdb")
# db = mongo_client["tweetdb"]
# collection = db["tweets"]

mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
db = mongo_client["tweetdb"]
collection = db["tweets"]


# Suppress FutureWarnings from transformer and wait for the model to be loaded
print(" Waiting for the model to be loade ...")
warnings.filterwarnings("ignore", category=FutureWarning)
# tweets = [
        # '@gabptsch pas moi #depression',
        # "Je souffre d'un nouveau symptôme dans ma #depression et mon #anxietegeneralisee : le trouble dissociatif 🙏🙏🙏 https://t.co/e0ZVVNDOqu",
        # 'Bordel ça craint cette pénurie danti depresseur...',
        # "J'ai encore un peu de marge mais ça n'a pas l'air de vouloir s'arranger...Forces à vous ❤️",
        # '#depression #penurie',
        # 'je viens de finir death note #depression #tuezmoi #jelererecommnceraiplus',
        # 'J’ai 0 photos.. j’ai que des screens… #depression #blocus https://t.co/5csKgqZK177 à 9 h de sommeil = 22 % de tristesse en moins.',
        # 'C’est prouvé.',
        # 'Prendre soin de son sommeil, c’est prendre soin de sa santé mentale.',
        # '#Neuvacure #sommeil #depression #anxiete #bienetre #france #belgique #suisse https://t.co/Kw387BQAn2',
        # 'Des chercheurs ont remarqué que les jeunes souffrant de dépression avaient des concentrations plus élevés de 9 microARN dans le sang.',
        # '#dépression #biomarqueurs #adolescents',
        # 'https://t.co/QMbUEwhR7G',
        # 'mon collègue pref qui démissionne .. avec qui je vais critiquer le taff mtn #dépression 😔',
        # 'Vous voulez que je fais une #Dépression de Sexe; Oh #Putain je crois que j’ai brisé le cœur de ma pharmacienne #Coccinelle blanche, ce matin pour que je matte pas c’est fesses elle c’est garé derrière ma rue…',
        # "Mais putain c trop je peux pas scroll sur Twitter sans que je vois un tweet de quelqu'un parler de notre défaite c trop une dinguerie, j'essaie d'oublier mais ils me laissent pas.",
        # '#dépression'
    # ]
app = Flask(__name__, template_folder='templates')


# # Twitter API credentials
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAM0u2AEAAAAAPaM0RKJ8z%2FjzcMleSn5%2BzN%2BqQyk%3DYERejFaH9IdkcAAzHQYijlyFzjJzUnUPInDCGoI1LROWDE9hnM'

# def get_tweets(query="#Depression lang:fr", max_results=30):
#     client = tweepy.Client(bearer_token=bearer_token)
#     try:
#         tweets = client.search_recent_tweets(query=query, max_results=max_results)
#         return [tweet.text for tweet in tweets.data] if tweets.data else []
#     except tweepy.TooManyRequests:
#         print("Too many requests. Sleeping for 15 minutes...")
#         time.sleep(15 * 60)
#         return get_tweets(query, max_results)

def clean_tweet(tweet):
    # Remove URLs, mentions, and hashtags
    tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
    # Remove mentions and hashtags
    tweet = re.sub(r'@\w+', '', tweet)
    # Remove hashtags but keep the text
    tweet = re.sub(r'#\w+', '', tweet)
    # Remove punctuatio and special characters
    tweet = re.sub(r'[^\w\s]', '', tweet)
    return tweet.strip()

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# def detect_theme(text):
#     thm = {
#         "solitude": ["seul", "solitude", "isolé", "isolée", "seule"],
#         "soutien": ["soutien", "aider", "entraide", "écoute", "force", "forces"],
#         "symptômes": ["symptôme", "symptômes", "tristesse", "fatigue", "dissociatif", "anxiété", "dépression", "depression"],
#         "médicament": ["médicament", "médicaments", "antidépresseur", "antidepresseur" ]
       
#     }
#     foundedword = []
#     for k, w in thm.items():
#         for s in w:
#             if s in text:
#                 foundedword.append(k)
#                 break
#     return foundedword if foundedword else ["autre"]
pipe = pipeline("text-classification", model="neuroapps/sentiments_classifier")
# for theme classification
theme_pipe = pipeline("text-classification", model="JTH/twitter_classification")     

@app.route('/tweet', methods=['GET'])
def tweet_by_index():
    print("############################################################################################################")
    print("starting depression tweets  analysis")
    tweets = [
        '@gabptsch pas moi #depression',
        "Je souffre d'un nouveau symptôme dans ma #depression et mon #anxietegeneralisee : le trouble dissociatif 🙏🙏🙏 https://t.co/e0ZVVNDOqu",
        'Bordel ça craint cette pénurie danti depresseur...',
        "J'ai encore un peu de marge mais ça n'a pas l'air de vouloir s'arranger...Forces à vous ❤️",
        '#depression #penurie',
        'je viens de finir death note #depression #tuezmoi #jelererecommnceraiplus',
        'J’ai 0 photos.. j’ai que des screens… #depression #blocus https://t.co/5csKgqZK177 à 9 h de sommeil = 22 % de tristesse en moins.',
        'C’est prouvé.',
        'Prendre soin de son sommeil, c’est prendre soin de sa santé mentale.',
        '#Neuvacure #sommeil #depression #anxiete #bienetre #france #belgique #suisse https://t.co/Kw387BQAn2',
        'Des chercheurs ont remarqué que les jeunes souffrant de dépression avaient des concentrations plus élevés de 9 microARN dans le sang.',
        '#dépression #biomarqueurs #adolescents',
        'https://t.co/QMbUEwhR7G',
        'mon collègue pref qui démissionne .. avec qui je vais critiquer le taff mtn #dépression 😔',
        'Vous voulez que je fais une #Dépression de Sexe; Oh #Putain je crois que j’ai brisé le cœur de ma pharmacienne #Coccinelle blanche, ce matin pour que je matte pas c’est fesses elle c’est garé derrière ma rue…',
        "Mais putain c trop je peux pas scroll sur Twitter sans que je vois un tweet de quelqu'un parler de notre défaite c trop une dinguerie, j'essaie d'oublier mais ils me laissent pas.",
        '#dépression'
    ]
    results = []
    for t in tweets:
        cleand = clean_tweet(t)
        normalized = normalize_text(cleand)
        print(f"Tweet: {t}\n  => Cleaned: {normalized}  \n", flush=True )
        sentiment = pipe(normalized)
        tps = theme_pipe(normalized)
        themes_detect = [tp['label'] for tp in tps if tp['score'] > 0.3]
    
        doc = {
            "original": t,
            "cleaned": normalized,
            "sentiment": sentiment[0]['label'],
            "score": sentiment[0]['score'],
            "themes": themes_detect
        }
        results.append(doc)
        collection.insert_one(doc)
    return render_template("tweets.html", results=results)
   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)




