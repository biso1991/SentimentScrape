import itertools
import requests
import time
import re
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, AutoModel
import torch
import warnings
from pymongo import MongoClient
from config import MODEL_NAME, INV_LABEL_MAP
import os
from utils import export_train_data

mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
db = mongo_client["tweetdb"]
collection = db["tweets"]

warnings.filterwarnings("ignore", category=FutureWarning)

def clean_tweet(tweet):
    tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
    tweet = re.sub(r'@\w+', '', tweet)
    tweet = re.sub(r'#\w+', '', tweet)
    tweet = re.sub(r'[^\w\s]', '', tweet)
    return tweet.strip()

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

bearer_tokens = [
    'AAAAAAAAAAAAAAAAAAAAADiH2QEAAAAAfqwR9kgIwJYGc%2FieNaTXxuHjS3g%3Dqkg14aLY01ykG6ggeGZkVQ6TqRNWUjKQImNJYYQZZxGtiRPDVx',
    'AAAAAAAAAAAAAAAAAAAAAGSI2QEAAAAAGKAAXVvtMrJvs8UwD8EC%2FhA5fzs%3DFRoYJnLhfaAPbocVtzEhTG5lCSqii5hMuDb2lCeZkP5p6JOkGp'
]
token_cycle = itertools.cycle(bearer_tokens)

def call_twitter_api(hashtag, max_total=10):
    url = 'https://api.twitter.com/2/tweets/search/recent'
    tweets = []
    next_token = None

    # Load model/tokenizer INSIDE the function
    model_path = "./fine_tuned_model" if os.path.exists("./fine_tuned_model") else MODEL_NAME
    sentiment_tokenizer = AutoTokenizer.from_pretrained(model_path)
    sentiment_model = AutoModelForSequenceClassification.from_pretrained(model_path)

    while len(tweets) < max_total:
        all_rate_limited = True
        for _ in range(len(bearer_tokens)):
            bearer_token = next(token_cycle)
            headers = {'Authorization': f'Bearer {bearer_token}'}
            params = {
                'query': f'#{hashtag}',
                'max_results': min(10, max_total - len(tweets))
            }
            if next_token:
                params['next_token'] = next_token

            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 429:
                continue
            elif response.status_code != 200:
                return {'error': response.text}

            all_rate_limited = False
            data = response.json()
            tweets.extend(data.get('data', []))
            next_token = data.get('meta', {}).get('next_token')
            break

        if all_rate_limited:
            time.sleep(2 * 60)
        if not next_token:
            break

    results = []
    for t in tweets:
        cleand = clean_tweet(t['text'])
        normalized = normalize_text(cleand)
        inputs = sentiment_tokenizer(normalized, return_tensors="pt")
        outputs = sentiment_model(**inputs)
        predicted_class = outputs.logits.argmax().item()
        sentiment_label = INV_LABEL_MAP.get(predicted_class, "UNKNOWN")
        score = float(outputs.logits.softmax(dim=1).max().item())
        doc = {
            "original": t,
            "cleaned": normalized,
            "sentiment": sentiment_label,
            "score": score,
            "themes": [sentiment_label]
        }
        results.append(doc)
        collection.insert_one(doc)
        export_train_data()
    return results

def download_hf_model(model_name_or_link, save_dir):
    try:
        # Convert Hugging Face link to model name if needed
        if model_name_or_link.startswith("https://huggingface.co/"):
            model_name = model_name_or_link.replace("https://huggingface.co/", "").strip("/")
        else:
            model_name = model_name_or_link.strip()
        os.makedirs(save_dir, exist_ok=True)
        AutoModel.from_pretrained(model_name, cache_dir=save_dir)
        AutoTokenizer.from_pretrained(model_name, cache_dir=save_dir)
        AutoConfig.from_pretrained(model_name, cache_dir=save_dir)
        print(f"Downloaded {model_name} to {save_dir}")
        return f"Downloaded {model_name} to {save_dir}"
    except Exception as e:
        print(f"Error downloading {model_name_or_link}: {e}")
        return f"Error downloading {model_name_or_link}: {e}"