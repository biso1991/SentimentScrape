from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, flash
from pymongo import MongoClient
from redis import Redis
from rq import Queue
from worker import call_twitter_api
import re
from markupsafe import Markup
from config import LABEL_MAP
import os
import datetime
from transformers import AutoModel, AutoTokenizer, AutoConfig
# import shutil
from worker import download_hf_model


app = Flask(__name__)
app = Flask(__name__)
app.secret_key = "123456"  
redis_conn = Redis(host='redis', port=6379)
queue = Queue('tweets', connection=redis_conn)

@app.template_filter('hashtag_icon')
def hashtag_icon_filter(text):
    return Markup(re.sub(r"(#\w+)", r'<i class="fa-solid fa-hashtag"></i> \1', text))

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

def parse_report_summary(file_path):
    summary = {
        "filename": os.path.basename(file_path),
        "date": None,
        "dataset": None,
        "num_examples": None,
        "base_model": None,
        "epochs": None,
        "learning_rate": None,
        "status": None,
        "accuracy": None,
        "loss": None,
        "f1": None,
        "model_size": None,
        "model_url": None,
        "user": None,
    }
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Dataset:" in line:
                    summary["dataset"] = line.split("Dataset:")[1].strip()
                if "Num examples:" in line:
                    summary["num_examples"] = line.split("Num examples:")[1].strip()
                if "Base model:" in line:
                    summary["base_model"] = line.split("Base model:")[1].strip()
                if "Epochs:" in line:
                    summary["epochs"] = line.split("Epochs:")[1].strip()
                if "Learning rate:" in line:
                    summary["learning_rate"] = line.split("Learning rate:")[1].strip()
                if "Status:" in line:
                    summary["status"] = line.split("Status:")[1].strip()
                if "Model size:" in line:
                    summary["model_size"] = line.split("Model size:")[1].strip()
                if "Model URL:" in line:
                    summary["model_url"] = line.split("Model URL:")[1].strip()
                if "User:" in line:
                    summary["user"] = line.split("User:")[1].strip()
                if "'eval_accuracy':" in line:
                    try:
                        acc = float(line.split("'eval_accuracy':")[1].split(",")[0].strip())
                        summary["accuracy"] = round(acc * 100, 2)
                    except:
                        summary["accuracy"] = None
                if "'eval_loss':" in line:
                    try:
                        loss = float(line.split("'eval_loss':")[1].split(",")[0].strip())
                        summary["loss"] = round(loss, 4)
                    except:
                        summary["loss"] = None
                if "'eval_f1':" in line:
                    try:
                        f1 = float(line.split("'eval_f1':")[1].split(",")[0].strip())
                        summary["f1"] = round(f1 * 100, 2)
                    except:
                        summary["f1"] = None
        summary["date"] = os.path.getmtime(file_path)
    return summary

@app.route('/search_tweets', methods=['POST'])
def search_tweets_form():
    hashtag = request.form.get('hashtag')
    max_total = int(request.form.get('max_total', 10))
    if not hashtag:
        return render_template('alert.html', message="Hashtag requis", status="danger")
    job = queue.enqueue(call_twitter_api, hashtag, max_total, job_timeout=600)
    return redirect(url_for('show_result', job_id=job.get_id(), hashtag=hashtag))

@app.route('/show_result/<job_id>')
def show_result(job_id):
    hashtag = request.args.get('hashtag', '')
    job = queue.fetch_job(job_id)
    if job is None:
        return render_template('alert.html', message="Job introuvable", status="danger")
    if job.is_finished:
        mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
        db = mongo_client["tweetdb"]
        collection = db["tweets"]
        tweets = list(collection.find({"original.text": {"$regex": hashtag, "$options": "i"}}).sort("_id", -1).limit(100))
        return render_template('tweets.html', tweets=tweets, hashtag=hashtag)
    elif job.is_failed:
        return render_template('alert.html', message="Erreur lors du traitement du job.", status="danger")
    elif job.is_queued:
        return render_template('alert.html', message=f"Recherche en file d'attente pour #{hashtag}... Veuillez patienter.", status="info")
    elif job.is_started:
        return render_template('alert.html', message=f"Recherche en cours pour #{hashtag}... Veuillez patienter.", status="warning")
    else:
        return render_template('alert.html', message="Statut du job inconnu.", status="secondary")

@app.route('/tweets')
def show_tweets():
    mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
    db = mongo_client["tweetdb"]
    collection = db["tweets"]
    tweets = list(collection.find().sort("_id", -1).limit(100))
    return render_template('tweets.html', tweets=tweets)

@app.route('/retrain_report')
def retrain_report():
    reports_dir = os.path.dirname(__file__)
    reports = []
    summaries = []
    for fname in sorted(os.listdir(reports_dir), reverse=True):
        if (fname.startswith("retrain_report_") and fname.endswith(".txt")) or fname == "retrain_report.txt":
            reports.append(fname)
            summaries.append(parse_report_summary(os.path.join(reports_dir, fname)))
    if reports:
        return redirect(url_for('show_retrain_report', filename=reports[0]))
    return render_template("retrain_report.html", reports=reports, report_content="", selected_report=None, summaries=summaries)

@app.route('/retrain_report/<filename>')
def show_retrain_report(filename):
    reports_dir = os.path.dirname(__file__)
    file_path = os.path.join(reports_dir, filename)
    report_content = ""
    pie_labels = []
    pie_precision = []
    pie_recall = []
    pie_f1 = []
    pie_support = []
    confusion_matrix = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            report_content = "".join(lines)
            # Parse classification report for bar chart
            start = False
            for line in lines:
                if "precision" in line and "recall" in line:
                    start = True
                    continue
                if start:
                    if line.strip() == "":
                        continue
                    parts = re.split(r"\s+", line.strip())
                    if len(parts) == 5 and not parts[0].startswith("avg"):
                        pie_labels.append(parts[0])
                        try:
                            pie_precision.append(float(parts[1]))
                        except:
                            pie_precision.append(0)
                        try:
                            pie_recall.append(float(parts[2]))
                        except:
                            pie_recall.append(0)
                        try:
                            pie_f1.append(float(parts[3]))
                        except:
                            pie_f1.append(0)
                        try:
                            pie_support.append(int(parts[4]))
                        except:
                            pie_support.append(0)
                    if parts and parts[0] in ("micro", "macro", "weighted"):
                        break
            # Parse confusion matrix
            for idx, line in enumerate(lines):
                if "Confusion Matrix" in line:
                    for mat_line in lines[idx+1:]:
                        if "[" in mat_line and "]" in mat_line:
                            row = [int(x) for x in mat_line.strip().replace("[", "").replace("]", "").split()]
                            confusion_matrix.append(row)
                        else:
                            break
    # List all reports and summaries for the sidebar and summary table
    reports = []
    summaries = []
    for fname in sorted(os.listdir(reports_dir), reverse=True):
        if (fname.startswith("retrain_report_") and fname.endswith(".txt")) or fname == "retrain_report.txt":
            reports.append(fname)
            summaries.append(parse_report_summary(os.path.join(reports_dir, fname)))
    return render_template(
        "retrain_report.html",
        reports=reports,
        report_content=report_content,
        selected_report=filename,
        pie_labels=pie_labels,
        pie_precision=pie_precision,
        pie_recall=pie_recall,
        pie_f1=pie_f1,
        pie_support=pie_support,
        summaries=summaries,
        confusion_matrix=confusion_matrix
    )

@app.route('/')
def home():
    return render_template('home.html')

# Example: store these in a database or global variable in production
api_stats = {
    "api_calls": 0,
    "tweets_analyzed": 0,
    "model_accuracy": 0.0
}

@app.before_request
def count_api_calls():
    api_stats["api_calls"] += 1

@app.route('/api/monitoring')
def api_monitoring():
    reports_dir = os.path.dirname(__file__)
    mongo_client = MongoClient("mongodb://mongoadmin:mongopass@mongodb:27017/")
    db = mongo_client["tweetdb"]
    tweets_count = db["tweets"].count_documents({})
    api_stats["tweets_analyzed"] = tweets_count
    try:
        with open(os.path.join(reports_dir, "retrain_report.txt"), "r", encoding="utf-8") as f:
            for line in f:
                if "'eval_accuracy':" in line:
                    acc = float(line.split("'eval_accuracy':")[1].split(",")[0].strip())
                    api_stats["model_accuracy"] = round(acc * 100, 2)
    except Exception:
        api_stats["model_accuracy"] = 0.0
    return jsonify(api_stats)

@app.route('/api/model_report')
def api_model_report():
    reports_dir = os.path.dirname(__file__)
    report_path = os.path.join(reports_dir, "retrain_report.txt")
    if not os.path.exists(report_path):
        return jsonify({"table": [], "pie": {}})
    with open(report_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    table_lines = []
    start = False
    for line in lines:
        if "precision" in line and "recall" in line:
            start = True
            continue
        if start and line.strip() == "":
            break
        if start:
            table_lines.append(line.strip())
    headers = ["label", "precision", "recall", "f1-score", "support"]
    table = []
    pie_labels = []
    pie_support = []
    for row in table_lines:
        parts = re.split(r"\s+", row)
        if len(parts) == 5:
            table.append(dict(zip(headers, parts)))
            pie_labels.append(parts[0])
            try:
                pie_support.append(int(parts[4]))
            except:
                pie_support.append(0)
    return jsonify({"table": table, "pie": {"labels": pie_labels, "support": pie_support}})
from flask import flash


@app.route('/models', methods=['GET', 'POST'])
def manage_models():
    models_dir = os.path.join(os.path.dirname(__file__), "uploaded_models")
    os.makedirs(models_dir, exist_ok=True)
    models = []
    for fname in os.listdir(models_dir):
        if fname != "huggingface_models.txt":
            models.append({"type": "upload", "name": fname, "path": os.path.join("uploaded_models", fname)})
    hf_models_path = os.path.join(models_dir, "huggingface_models.txt")
    if os.path.exists(hf_models_path):
        with open(hf_models_path, "r", encoding="utf-8") as f:
            for line in f:
                models.append({"type": "huggingface", "name": line.strip(), "path": line.strip()})
    if request.method == 'POST':
        if 'model_file' in request.files and request.files['model_file'].filename:
            file = request.files['model_file']
            save_path = os.path.join(models_dir, file.filename)
            file.save(save_path)
            flash(f"Modèle uploadé: {file.filename}", "success")
        elif 'hf_model_link' in request.form and request.form['hf_model_link']:
            link = request.form['hf_model_link'].strip()
            if link.startswith("https://huggingface.co/"):
                link = link.replace("https://huggingface.co/", "").strip("/")
            model_save_path = os.path.join(models_dir, link.replace("/", "_"))
            queue.enqueue(download_hf_model, link, model_save_path)
            # Avoid duplicate entries
            if not os.path.exists(hf_models_path) or link not in open(hf_models_path).read():
                with open(hf_models_path, "a", encoding="utf-8") as f:
                    f.write(link + "\n")
            flash(f"Téléchargement du modèle Hugging Face lancé en tâche de fond: {link}", "info")
        else:
            flash("Aucun modèle sélectionné.", "danger")
        return redirect(url_for('manage_models'))
    return render_template('manage_models.html', models=models)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)