# Utiliser l'image Graphviz de base
FROM graphviz/graphviz

# Installer Python et pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . /app

# Installer les dépendances Python
RUN pip3 install -r requirements.txt

# Exposer le port 5000 pour Flask
# EXPOSE 5000

# Lancer l'application Flask
CMD ["python3", "main.py"]
