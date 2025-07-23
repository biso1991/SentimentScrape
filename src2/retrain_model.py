from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from config import MODEL_NAME, LABEL_MAP, INV_LABEL_MAP
import datetime
import os

# Connect to MongoDB
mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
db = mongo_client["tweetdb"]
collection = db["tweets"]

# Fetch labeled tweets
data = list(collection.find({"sentiment": {"$in": list(LABEL_MAP.keys())}}))
texts = [d["cleaned"] for d in data]
labels = [LABEL_MAP[d["sentiment"]] for d in data]

if len(texts) < 3:
    print("Not enough data to retrain.")
    exit(1)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# Tokenization
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
train_encodings = tokenizer(X_train, truncation=True, padding=True, max_length=128)
test_encodings = tokenizer(X_test, truncation=True, padding=True, max_length=128)

class TweetDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

train_dataset = TweetDataset(train_encodings, y_train)
test_dataset = TweetDataset(test_encodings, y_test)

# Model and training setup
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(LABEL_MAP))

training_args = TrainingArguments(
    output_dir="./fine_tuned_model",
    num_train_epochs=2,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir='./logs',
    learning_rate=2e-5,
    load_best_model_at_end=True,
    metric_for_best_model="eval_accuracy",
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred.
    preds = np.argmax(logits, axis=1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
eval_results = trainer.evaluate()
print("Evaluation results:", eval_results)

# Predictions and report
preds = trainer.predict(test_dataset)
y_pred = np.argmax(preds.predictions, axis=1)

report = classification_report(
    y_test,
    y_pred,
    labels=list(range(len(LABEL_MAP))),
    target_names=list(LABEL_MAP.keys())
)

print(report)

# Save model and tokenizer
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

# Save results to a timestamped file
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
report_filename = f"retrain_report_{timestamp}.txt"
with open(report_filename, "w", encoding="utf-8") as f:
    f.write("Dataset: MongoDB tweets\n")
    f.write(f"Base model: {MODEL_NAME}\n")
    f.write(f"Epochs: {training_args.num_train_epochs}\n")
    f.write(f"Learning rate: {training_args.learning_rate}\n")
    f.write("Status: Success\n")
    f.write("User: auto\n\n")
    f.write("Evaluation results:\n")
    f.write(str(eval_results) + "\n\n")
    f.write("Classification report:\n")
    f.write(report)
print(f"Retraining report saved to {report_filename}")

# Optionally, also save as retrain_report.txt for app compatibility
with open("retrain_report.txt", "w", encoding="utf-8") as f:
    f.write("Dataset: MongoDB tweets\n")
    f.write(f"Base model: {MODEL_NAME}\n")
    f.write(f"Epochs: {training_args.num_train_epochs}\n")
    f.write(f"Learning rate: {training_args.learning_rate}\n")
    f.write("Status: Success\n")
    f.write("User: auto\n\n")
    f.write("Evaluation results:\n")
    f.write(str(eval_results) + "\n\n")
    f.write("Classification report:\n")
    f.write(report)