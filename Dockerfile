
FROM python:3.14-slim

WORKDIR /app

# Copier le fichier de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'API
COPY ./api /app

EXPOSE 5000
CMD ["python", "app.py"]
