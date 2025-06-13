FROM python:3.11-slim as base

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

From base as final
RUN pip install emoji==0.6.0
# RUN apt-get update && apt-get install -y iputils-ping
# RUN pip install --upgrade numpy==1.24.4 scikit-learn==1.3.0

CMD ["python", "src2/app.py"]