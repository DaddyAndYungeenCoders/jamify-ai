FROM python:3.9.21-bookworm

#RUN apt install gcc musl-dev g++ libffi-dev


RUN mkdir "/repo"

COPY ./requirements.txt /repo
COPY ./run.py /repo
COPY ./app /repo/app

# Installer curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Définir les variables d'environnement
ENV S3_BASE_URL=https://jamifybucket.s3.eu-north-1.amazonaws.com/glove_vectors
ENV SPACY_MODEL_DIR=/repo/glove_vectors
RUN mkdir "/repo/glove_vectors"
RUN mkdir "/repo/glove_vectors/vocab"

# Liste des fichiers nécessaires pour les vecteurs SpaCy
ENV GLOVE_VECTOR_FILES="config.cfg meta.json tokenizer vocab/key2row vocab/lookups.bin vocab/strings.json vocab/vectors vocab/vectors.cfg"

# Créer le répertoire pour les vecteurs
RUN mkdir -p ${SPACY_MODEL_DIR}

# Télécharger les fichiers nécessaires
RUN for file in ${GLOVE_VECTOR_FILES}; do \
    curl -o ${SPACY_MODEL_DIR}/$file ${S3_BASE_URL}/$file; \
done

WORKDIR /repo

RUN python3 -m pip install --upgrade pip
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install -r requirements.txt



ENV BDHOST=localhost
ENV DBNAME=jamify
ENV DBUSER=admin
ENV DBPASS=admin
ENV QUEHOST=localhost
ENV QUEPORT=616162
ENV QUEUSER=admin
ENV QUEPASS=admin

CMD python3 run.py