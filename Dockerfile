# Basis-Image
FROM tensorflow/tensorflow:2.9.1-gpu

# Arbeitsverzeichnis im Container
WORKDIR /app

# Python 3.9 installieren und als Standard setzen
RUN apt-get update && apt-get install -y python3.9 python3.9-distutils \
    && ln -sf /usr/bin/python3.9 /usr/bin/python3

# Pip aktualisieren
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Kopiere die Abhängigkeiten und den Quellcode
COPY requirements.txt .
COPY . .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Standard-Befehl, um den Bot auszuführen
CMD ["python3", "main.py"]
