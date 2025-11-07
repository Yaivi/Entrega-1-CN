FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

ENV FLASK_ENV=production

# Puerto donde Flask 
EXPOSE 8080


CMD ["python", "main.py"]
