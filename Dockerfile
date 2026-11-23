# 1. Image de base Python légère
FROM python:3.11-slim

# 2. Dossier de travail dans le conteneur
WORKDIR /app

# 3. Copie et installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie du code source de l'application
COPY app.py .

# 5. Exposition du port 8000
EXPOSE 8000

# 6. Commande de lancement
CMD ["python", "app.py"]