# Analyse des Tweets avec Flask, Mongodb et Docker

Ce projet analyse des tweets  sur la dépression, affiche leur sentiment(positif/négatif) et propose une interfaceweb simple pour visualiser les résultas.

---

## Sommaire:

- [Description](#fonctionnalités)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation &amp; Lancement](#installation--lancement)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Troubleshooting ](#dépannage)
- [Liens vers des modèles  sur Hugging Face](#dépannage)

## Description de l'application:

* J’ai créé une liste de tweets a analyser.
* Avant l’analyse, j’ai effectué un nettoyage des données (cleaning) sur les tweets en utilisant des **regex** pour enlever les caractère spéciaux, les liens, mentions, etc., afin d’améliorer la qualité des résultat
* Ensuite,j’ai développe une app flask qui effectue une analyse de sentiment et détecté les thèmes sur chaque tweet nettoyé, en utilisant les modèles Huggingface(neuroapps/sentiments_classifier et JTH/twitter_classification ).
* Pour faciliter le déploiement,j’ai créé un Dockerfile pour construire l’image de l’application Flask.
* J’ai aussi configuré un docker-compose.yml qui lance deux service :

  * flaskapp (l’application Flask  )
  * mongodb (la base de données  )
* Afin d’assurer que l’application Flask ne démarre  qu’après le lancement de MongoDB , j’ai ajouté un script wait_for_mongodb dans le service flasapp.ce script attend la disponibilité de MongoDB avant de lancer l’app Flask, évitant ainsi des erreur de connexion

---

## Fonctionnalités

- Nettoyage et normalisation de tweets.
- Analyse de sentiment via un modèle HuggingFace.
- Affichage des résultats dans les logs et sur une page web HTML/CSS.
- Déploiement  avec Docker_Compose (Flask + MongoDB)

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker_Compose
  ](https://docs.docker.com/compose/install/)

---

## Installation & Lancement

Absolutely, Bilel. Here's a **professionally written "Content Architecture" section** that you can directly include in your `README.md`. It uses clear technical language, proper formatting, and is suitable for GitHub, portfolios, or documentation.

---

## 🧱 Content Architecture

The `TweetSentimentAnalyzer` is built using a **modular, containerized full-stack architecture** that enables real-time sentiment analysis, model retraining, and insightful visualization of Twitter data.

This architecture includes the following core components:

---

### 1. 🔗 Backend – Flask API (`backend/`)

A Python-based RESTful API built with  **Flask** , responsible for the application’s data and ML logic.

**Responsibilities:**

* Serve sentiment predictions via pre-trained or fine-tuned transformer models
* Trigger asynchronous model retraining using Celery
* Interface with MongoDB for tweet storage and report management
* Expose REST endpoints for use by the Angular frontend

**Key Modules:**

| File                 | Purpose                                             |
| -------------------- | --------------------------------------------------- |
| `app.py`           | Main Flask app, routes and API logic                |
| `worker.py`        | Background worker for retraining (Celery)           |
| `retrain_model.py` | Fine-tuning and evaluation logic for NLP models     |
| `config.py`        | Configuration for model paths, database URIs, etc.  |
| `utils.py`         | Text cleaning, preprocessing, and utility functions |
| `requirements.txt` | Python dependencies                                 |

---

### 2. 🎨 Frontend – Angular SPA (`frontend/`)

A responsive **Single Page Application (SPA)** built with Angular, providing a rich user interface for interaction and monitoring.

**Responsibilities:**

* Enable tweet search by hashtags
* Visualize sentiment and theme analysis
* Manage and upload transformer models
* Trigger model retraining
* Download and review training reports

**Key Modules:**

| File / Directory      | Purpose                                   |
| --------------------- | ----------------------------------------- |
| `src/app/pages/`    | UI components: Dashboard, Reports, Models |
| `src/app/services/` | Handles HTTP communication with Flask API |
| `Dockerfile`        | Frontend container setup                  |
| `angular.json`      | Build and config management               |

---

### 3. 🗄️ Database – MongoDB

MongoDB is used as a **NoSQL document store** for:

* Persisting raw and cleaned tweets
* Caching hashtag search results
* Storing metadata on models and retraining reports

**MongoDB** is containerized and managed via Docker Compose.

---

### 4. 🤖 Model Management

The project utilizes **Hugging Face Transformers** for NLP tasks. Models are either pre-trained, linked via Hugging Face, or fine-tuned using in-app data.

**Model lifecycle:**

* Load models at runtime for inference
* Fine-tune models using user data via background jobs
* Store trained weights in the `fine_tuned_model/` directory

---

### 5. 📊 Reporting & Monitoring

Training and evaluation metrics are stored as plain text in:

```
retrain_reports/
├── retrain_report.txt
├── retrain_report_<timestamp>.txt
```

These reports include:

* Accuracy, precision, recall, F1-score
* Loss evolution and evaluation metrics
* Training timestamps and model IDs

Reports can be downloaded from the frontend or via the API.

---

### 6. 🐳 Containerization & Deployment

All services run in **Docker containers** orchestrated using `docker-compose`.

**Service Overview:**

| Service    | Container Name | Port  | Description        |
| ---------- | -------------- | ----- | ------------------ |
| Flask API  | `flaskapp`   | 8000  | RESTful backend    |
| Angular UI | `frontend`   | 4200  | Web user interface |
| MongoDB    | `mongodb`    | 27017 | Document database  |

Docker Compose handles:

* Multi-service orchestration
* Network isolation
* Shared volumes and environment management

---

### 🔁 System Workflow

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
   Celery (for retraining)
          ↓
 Hugging Face Fine-tuning
```

---

## 📌 Summary

This architecture enables real-time sentiment analysis and theme extraction from tweets, while supporting continuous improvement of NLP models through on-demand retraining. It is fully portable and production-ready due to its containerized, service-oriented design.

---

Let me know if you’d like a  **visual architecture diagram** , or if you want this turned into a PDF or slide for presentation/documentation purposes.

1. **Crée un dossier nommeExercice_journée_observation**

```bash
Linux: mkdir Exercice_journée_observation &&
   cd Exercice_journée_observation
```

2. **Vérifiez la struture**

   - `src2/app.py` : code principal flask
   - `src2/templates/tweets.html` : template HTML
   - `docker-compose.yml and dockerfile`: configuration Doker
3. **Lancez les services**

   ```bash
   docker-compose up --build
   mongo conatainer 
   docker exec -it exercice_journe_observation-mongodb-1 mongosh -u mongoadmin -p mongopas
     use tweetdb 
     db.tweets.countDocuments()
     db.tweets.find().pretty()
   flask container 
   docker exec -it exercice_journe_observation-flaskapp-1 
   docker logs -f exercice_journe_observation-flaskapp-1 

   ```

   Cela démarre MongoDB et Flask.

   <img src="real_images/3.png" alt="Erreur MongoDB" width="355"/>
   <img src="real_images/34.png" alt="Erreur MongoDB 2" width="355"/>
   <img src="real_images/33.png" alt="Authentification échouée" width="355"/>
   <img src="real_images/32.png" alt="Timeout pip" width="355"/>
   <img src="real_images/31.png" alt="Docker pip timeout" width="355"/>
   <img src="real_images/4.png" alt="Problème docker-compose" width="355"/>
   <img src="real_images/5.png" alt="Téléchargement wrapt" width="355"/>
   <img src="real_images/6.png" alt="Erreur Gensim pip" width="355"/>
4. **Accédez à l’application et mongo database**
   Ouvrez [http://localhost:8000/tweet](http://localhost:8000/tweet) dans votre navigateur.

   <img src="/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/50.png" alt="Image 1" width="1000"/>

---

## Utilisation

- **Page Web** :Les tweets, leur version nettoyée et leur sentiment s’affichent joliment sur la page `/tweet`.
- **Logs en temps réel  et controle leur container via makefile et dokcer-compose :**
  Pour voir les détails dans le terminal :

  ```docker

  controle via docker-compose:
      docker-compose up -d
      docker-compose build
      docker-compose down 
      docker exec  -it exercice_journe_observation-flaskapp-1 bash


  ###########################################################################

  Contrôle via makefile
    make DOC_UP
    make DOC_BUILD
    make DOC_DOWN
    make flask_container
    make log_flask_container
    make List_docker_container
  #############################################################################

  docker exec -it exercice_journe_observation-mongodb-1 mongosh -u mongoadmin -p mongopass
  docker logs -f exercice_journe_observation-flaskapp-1

  ```

## Structure du projet

![1748435886106](image/readme/1748435886106.png)

# Troubleshooting

### 2. Problèmes de port (Port)

* **Error** : Port déjà utilisé et le port est déjà occupé par un autre service.
* **Solution** :
  * Identifiez quel service utilise ce port (`lsof -i :27017` sur Linux).
  * Changez le port dans votre configuration Docker et application.
  * Libérez le port en arêtant le service qui l’occupe.

---

### 3. Probl&me avec le token Twitter (API)

* **Erreur** : Authentifiation échouée ou delai d’attente.
* **Cause probable** :
  * Token expiré ou invalide.
  * Limite de requêtes atteinte.
  * Mauvaise gestion des exceptions dans le code.
* **Solution** :
  * Vérifiez que le token est valide et à jour.
  * Implémentez la gestion des erreurs et des retries dans votre code.
  * Respectez les limites d’API (rate limits).

---

### 4. Problèmes d’analyse de sentiments (Sentiment Analysis)

* **Erreur** : Modèle Huggingface met trop detemps à répondre ou génère une erreur.
  * chargement du modele lent.

### 5. Liens vers des modèles  sur Hugging Face

https://huggingface.co/JTH/twitter_classification?library=transformers

https://huggingface.co/neuroapps/sentiments_classifier=transformers

## **Les captures d’écran** des problèmes et

![Image 16](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/21.png)
![Image 1](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/22.png)
![Image 21](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/23.png)
![Image 22](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/24.png)
![Image 22](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/25.png)
![Image 22](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/26.png)
![Image 22](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/27.png)
![Image 22](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/28.png)![Image 22](/home/bilel/Desktop/elk_stack/Question3/Exercice_journée_observation/real_images/29.png)

**Remarque :**

certaines explications ou parties d'exercice n'ont pas pu etre rédigées ou ajoutée dans ce README par manque de temps. Merci de votre compréhension.
