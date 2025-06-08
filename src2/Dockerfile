FROM python:3.11-slim as base

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
From base as final
RUN pip install --default-timeout=300 gensim==4.3.1  nltk==3.8.1
CMD ["python", "src2/app.py"]