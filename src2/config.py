MODEL_NAME = "finiteautomata/bertweet-base-sentiment-analysis"
LABEL_MAP = {"NEGATIVE": 0, "NEUTRAL": 1, "POSITIVE": 2}
INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

MODEL_ID = "distilbert-base-uncased-finetuned-sst-2-english"
