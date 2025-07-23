
# Real-Time Emotion Analysis Suite

A full-stack platform for **real-time tweet sentiment analysis** using fine-tuned transformer models. This solution integrates a Flask backend, Angular frontend, MongoDB, and Hugging Face models — all containerized with Docker for easy deployment.

---

## Table of Contents

* [Getting Started](https://chatgpt.com/c/6880eb33-c3c0-8002-a71c-a61798d9c177#getting-started)
* [Project Structure](https://chatgpt.com/c/6880eb33-c3c0-8002-a71c-a61798d9c177#project-structure)
* [Usage](https://chatgpt.com/c/6880eb33-c3c0-8002-a71c-a61798d9c177#usage)
* [Content Architecture](https://chatgpt.com/c/6880eb33-c3c0-8002-a71c-a61798d9c177#content-architecture)
* [Troubleshooting](https://chatgpt.com/c/6880eb33-c3c0-8002-a71c-a61798d9c177#troubleshooting)
* [Model Links](https://chatgpt.com/c/6880eb33-c3c0-8002-a71c-a61798d9c177#model-links)

---

## Getting Started

### 1. Create project directory

```bash
mkdir Real_Time_Emotion_Analysis && cd Real_Time_Emotion_Analysis
```

### 2. Verify project structure

* `src2/app.py` — Main Flask backend
* `src2/templates/tweets.html` — HTML template (legacy)
* `docker-compose.yml` and `Dockerfile` — Docker configurations

### 3. Launch services

```bash
docker-compose up --build
```

* Access MongoDB container:

```bash
docker exec -it Real_Time_Emotion_Analysis-mongodb-1 mongosh -u mongoadmin -p mongopas
use tweetdb
db.tweets.countDocuments()
db.tweets.find().pretty()
```

* Access Flask container logs and terminal:

```bash
docker exec -it Real_Time_Emotion_Analysis-flaskapp-1 bash
docker logs -f Real_Time_Emotion_Analysis-flaskapp-1
```

### 4. Open application

Browse to [http://localhost:8000/tweet](http://localhost:8000/tweet) to view tweets and sentiment results.

---

## Usage

* **Web interface:** Search tweets by hashtag, view sentiment and cleaned text on `/tweet`.
* **Container management:** Control via `docker-compose` or `Makefile` commands:

```bash
docker-compose up -d
docker-compose build
docker-compose down

docker exec -it Real_Time_Emotion_Analysis-flaskapp-1 bash
docker logs -f Real_Time_Emotion_Analysis-flaskapp-1
```

Makefile shortcuts:

```bash
make DOC_UP
make DOC_BUILD
make DOC_DOWN
make flask_container
make log_flask_container
make List_docker_container
```

---

## Content Architecture

### 1. Backend – Flask API (`src2/`)

* RESTful API with Flask handling data processing and ML logic
* Provides sentiment predictions, triggers retraining jobs, interfaces with MongoDB
* Key files:

| File                 | Purpose                           |
| -------------------- | --------------------------------- |
| `app.py`           | Main Flask app & API routes       |
| `worker.py`        | Background job worker (Celery)    |
| `retrain_model.py` | Model fine-tuning and evaluation  |
| `config.py`        | Configuration settings            |
| `utils.py`         | Preprocessing & utility functions |

---

### 2. Frontend – Angular SPA (`frontend/`)

* Responsive Single Page Application for tweet sentiment visualization and model management
* Supports search, model upload, retraining triggers, and report downloads
* Key modules:

| Directory/File        | Purpose                                    |
| --------------------- | ------------------------------------------ |
| `src/app/pages/`    | UI components (Dashboard, Models, Reports) |
| `src/app/services/` | HTTP services to communicate with backend  |
| `Dockerfile`        | Frontend container configuration           |

---

### 3. Database – MongoDB

* NoSQL document store for raw and cleaned tweets, search caching, and model metadata
* Containerized and managed via Docker Compose

---

### 4. Model Management

* Uses Hugging Face Transformer models for NLP tasks
* Supports pre-trained, linked, or fine-tuned models
* Fine-tuned models saved under `fine_tuned_model/` directory

---

### 5. Reporting & Monitoring

* Training reports saved in `retrain_reports/` directory
* Includes accuracy, precision, recall, F1-score, loss evolution, and timestamps
* Downloadable via frontend or API endpoints

---

### 6. Containerization & Deployment

| Service    | Container Name | Port  | Description            |
| ---------- | -------------- | ----- | ---------------------- |
| Flask API  | `flaskapp`   | 8000  | RESTful backend server |
| Angular UI | `frontend`   | 4200  | Web user interface     |
| MongoDB    | `mongodb`    | 27017 | Database service       |

* Docker Compose orchestrates multi-container setup, networking, and environment configs.

---

### System Workflow

```plaintext
User → Angular Frontend
          ↓
     Flask REST API
          ↓
  ┌────────────┐     ┌──────────────┐
  │ Sentiment  │ ←→  │ MongoDB      │
  │ Inference  │     └──────────────┘
  │ & Reports  │
  └────────────┘
          ↓
   Celery (Background Retraining)
          ↓
 Hugging Face Model Fine-tuning
```

---

## Troubleshooting

### Port Conflicts

* **Error:** Port already in use
* **Fix:** Identify conflicting process (`lsof -i :27017`), stop it or change port in config files.

### Twitter API Token Issues

* **Error:** Authentication failure or timeouts
* **Fix:** Verify token validity, handle API rate limits, and add retries in code.

### Sentiment Analysis Delays

* **Error:** Slow or failing Hugging Face model responses
* **Fix:** Use optimized models, check resource allocation, and monitor model loading times.

---

## Model Links (Hugging Face)

* [JTH Twitter Classification](https://huggingface.co/JTH/twitter_classification)
* [Neuroapps Sentiment Classifier](https://huggingface.co/neuroapps/sentiments_classifier)
