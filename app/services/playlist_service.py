import os
import requests
import spacy
import json
import pandas as pd
import langid
from googletrans import Translator

from app.utils.constants import TAG_FIELD

from app import controllers
from app.utils.constants import TAG_FIELD
from app.utils.logger import logger

# URL du bucket S3 contenant les vecteurs SpaCy
S3_BASE_URL = "https://jamifybucket.s3.eu-north-1.amazonaws.com/glove_vectors"
SPACY_MODEL_DIR = "./glove_vectors"

# Liste des fichiers nécessaires pour les vecteurs SpaCy
GLOVE_VECTOR_FILES = [
    "config.cfg",
    "meta.json",
    "tokenizer",
    "vocab/key2row",
    "vocab/lookups.bin",
    "vocab/strings.json",
    "vocab/vectors",
    "vocab/vectors.cfg",
]

# def download_glove_vectors(base_url, target_dir, files):
#    """
#    Télécharge les fichiers nécessaires depuis un bucket S3.
#    """
#    if not os.path.exists(target_dir):
#        os.makedirs(target_dir)
#
#    for file_name in files:
#        file_url = f"{base_url}/{file_name}"
#        local_file_path = os.path.join(target_dir, file_name.replace("/", os.sep))
#
#        # Créer les sous-dossiers si nécessaire
#        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
#
#        if not os.path.exists(local_file_path):
#            print(f"Téléchargement de {file_name}...")
#            response = requests.get(file_url, stream=True)
#            if response.status_code == 200:
#                with open(local_file_path, "wb") as f:
#                    for chunk in response.iter_content(chunk_size=1024):
#                        f.write(chunk)
#                print(f"{file_name} téléchargé avec succès.")
#            else:
#                raise RuntimeError(f"Impossible de télécharger {file_name}. Erreur {response.status_code}.")
#        else:
#            print(f"{file_name} est déjà présent.")
#
#
## Télécharger tous les fichiers nécessaires
# download_glove_vectors(S3_BASE_URL, SPACY_MODEL_DIR, GLOVE_VECTOR_FILES)
#
# Charger les vecteurs convertis dans SpaCy
SPACY_MODEL = spacy.load(SPACY_MODEL_DIR)

# Vérification du chargement des vecteurs
if not SPACY_MODEL("music").has_vector:
    raise RuntimeError("Les vecteurs GloVe ne sont pas chargés correctement.")
else:
    logger.info("Les vecteurs GloVe sont bien chargés dans SpaCy.")

# Création du traducteur Google Translate
translator = Translator()



def detect_language(text):
    try:
        lang, _ = langid.classify(text)
        return lang
    except Exception as e:
        raise ValueError(f"Langue non prise en charge : {str(e)}")



def translate_to_english(text, lang):
    if lang != "en":
        translated = translator.translate(text, src=lang, dest="en")
        return translated.text
    return text



class PlaylistService:
    @staticmethod
    def generate_playlist(csv_file, keywords, name, description, number=None, job_id=None, user_id=None):
        """
        Génère une playlist basée sur la similarité des mots-clés avec les tags.
        """
        # Chargement des données CSV
        data = pd.read_csv(csv_file)
        tags = data[TAG_FIELD].dropna().unique()

        # Recherche de tags similaires
        similar_tags = set()
        for keyword in keywords:
            similar_tags.update(PlaylistService.find_similar_tags(keyword, tags))

        # Filtrer les musiques avec les tags similaires
        filtered_songs = data[data[TAG_FIELD].isin(similar_tags)]
        print(f"Tags similaires : {similar_tags}")

        # Limiter le nombre de musiques
        if number is not None:
            filtered_songs = filtered_songs.head(number)

        # Créer la réponse avec les IDs des musiques et les informations supplémentaires
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": {
                "musics": [song['id'] for song in filtered_songs.to_dict(orient='records')],
                "name": name,
                "description": description
            }
        }

        return playlist_end_job

    @staticmethod
    def find_similar_tags(user_input, tags):
        """
        Trouve des tags similaires au mot-clé en utilisant les vecteurs GloVe.
        """
        lang = detect_language(user_input)
        print(f"Langue détectée pour '{user_input}': {lang}")

        # Traduction si nécessaire
        translated_input = translate_to_english(user_input, lang)
        print(f"Mot-clé traduit en anglais : {translated_input}")

        similar_tags = []
        input_vector = SPACY_MODEL(translated_input.lower())

        if not input_vector.has_vector:
            print(f"Le mot '{translated_input}' n'a pas de vecteur.")
            return []

        seuils = [0.7, 0.6, 0.5]

        for seuil in seuils:
            for tag in tags:
                tag_words = tag.replace(" ", "").split(",")
                for word in tag_words:
                    tag_vector = SPACY_MODEL(word.lower())

                    if not tag_vector.has_vector:
                        continue

                    similarity = input_vector.similarity(tag_vector)

                    if similarity > seuil:
                        similar_tags.append(tag)
                        break

            if similar_tags:
                break

        print(f"Tags similaires trouvés : {similar_tags}")
        return similar_tags

    @staticmethod
    def consume_and_publish(message):
        """
        Fonction pour récupérer le message de la queue, générer la playlist, et publier le résultat.
        """


        try:
            # Décoder le message reçu (en supposant que le message est au format JSON)
            playlist_request = json.loads(message)
            print(f"Message reçu : {playlist_request}")

            # Extraire les informations nécessaires
            job_id = playlist_request.get('id')
            user_id = playlist_request.get('userId')
            keywords = playlist_request.get('keywords', [])
            name = playlist_request.get('name', 'Default Playlist Name')
            description = playlist_request.get('description', '')

            print(f"Traitement de la playlist pour Job ID: {job_id}, User ID: {user_id}")
            print(f"Keywords: {keywords}, Name: {name}, Description: {description}")

            # Vérifie si les champs obligatoires sont présents
            if not job_id or not user_id:
                raise ValueError("Les champs 'id' et 'userId' sont obligatoires dans le message.")
            csv_file = "app/playlist/music_tags_realistic.csv"

            # Générer la playlist
            playlist_end_job = PlaylistService.generate_playlist(
                csv_file, keywords, name, description, job_id=job_id, user_id=user_id
            )

            stomp = controllers.stomp

            logger.info(f"Playlist générée : {playlist_end_job}")

            # Publier le résultat dans la queue cible
            stomp.send_message(
                "com.jamify.orchestrator.playlist-done",
                json.dumps(playlist_end_job)
            )

            logger.info(f"Message envoyé à la queue 'com.jamify.orchestrator.playlist-done': {playlist_end_job}")

        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON pour le message : {message}")
        except Exception as e:
            print(f"Erreur lors du traitement du message : {e}")
