import os
import requests
import spacy
import json
import pandas as pd
import langid
from app.dto.music_dto import MusicDTO
from app.utils.logger import logger
from app.repository import Repository
from googletrans import Translator
from app import controllers
from app.utils.constants import TAG_FIELD

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
    def generate_playlist(keywords, name, description, number=None, job_id=None, user_id=None):
        """
        Génère une playlist basée sur la similarité des mots-clés avec les tags depuis la base de données.
        """
        logger.debug(f"Appel de generate_playlist avec : keywords={keywords}, name={name}, description={description}, number={number}, job_id={job_id}, user_id={user_id}")

        # Connexion à la base de données
        database = Repository()
        try:
            database.connect()
            logger.debug("Connexion à la base de données réussie.")

            if not database.music_repository:
                logger.error("FAILED TO CONNECT TO DATABASE, FAILED TO FETCH MUSIC")
                return None
            if not database.tags_repository:
                logger.error("FAILED TO CONNECT TO DATABASE, FAILED TO FETCH TAGS")
                return None

            # Récupération des tags disponibles
            tags = database.tags_repository.get_all_tags()
            logger.debug(f"Tags récupérés depuis la base de données : {tags}")

            if tags is None:
                logger.error("Les tags sont None.")
                return None

            tag_labels = [tag.name for tag in tags]
            logger.debug(f"Noms des tags extraits : {tag_labels}")

            # Recherche de tags similaires
            similar_tags = set()
            for keyword in keywords:
                similar_tags.update(PlaylistService.find_similar_tags(keyword, tags))

            logger.info(f"Tags similaires trouvés : {similar_tags}")

            # Récupération des musiques correspondant aux tags similaires
            filtered_songs = []
            for tag in similar_tags:
                # Recherche des musiques pour chaque tag
                songs_for_tag = database.tags_repository.get_musics_by_tag(tag)
                if songs_for_tag:
                    filtered_songs.extend(songs_for_tag)
            
            logger.debug(f"Musiques récupérées pour les tags similaires : {filtered_songs}")

            if not filtered_songs:
                logger.info("Aucune musique trouvée pour les tags similaires.")
                return None

            # Limiter le nombre de musiques
            if number is not None:
                filtered_songs = filtered_songs[:number]

            playlist_end_job = {
                "id": job_id,
                "userId": user_id,
                "data": {
                    "musics": filtered_songs,
                    "name": name,
                    "description": description
                }
            }
            logger.debug(f"Playlist générée avec succès : {playlist_end_job}")
            return playlist_end_job

        except Exception as e:
            logger.error(f"Erreur lors de la génération de la playlist : {e}")
            return None
        finally:
            database.disconnect()



    @staticmethod
    def find_similar_tags(user_input, tags):
        """
        Trouve des tags similaires au mot-clé en utilisant les vecteurs GloVe.
        """
        lang = detect_language(user_input)
        logger.info(f"Langue détectée pour '{user_input}': {lang}")

        # Traduction si nécessaire
        translated_input = translate_to_english(user_input, lang)
        logger.info(f"Mot-clé traduit en anglais : {translated_input}")

        similar_tags = []
        input_vector = SPACY_MODEL(translated_input.lower())

        if not input_vector.has_vector:
            logger.warning(f"Le mot '{translated_input}' n'a pas de vecteur.")
            return []

        seuils = [0.7, 0.6, 0.5]

        for seuil in seuils:
            for tag in tags:
                # Utilisation de l'attribut 'name' du TagDTO
                tag_words = tag.name.replace(" ", "").split(",")  # Accède au nom du tag
                for word in tag_words:
                    tag_vector = SPACY_MODEL(word.lower())

                    if not tag_vector.has_vector:
                        continue

                    similarity = input_vector.similarity(tag_vector)

                    if similarity > seuil:
                        similar_tags.append(tag.name)  # Ajoute le nom du tag similaire
                        break

            if similar_tags:
                break

        logger.info(f"Tags similaires trouvés : {similar_tags}")
        return similar_tags

    @staticmethod
    def consume_and_publish(message):
        """
        Fonction pour récupérer le message de la queue, générer la playlist, et publier le résultat.
        """
        try:
            playlist_request = json.loads(message)
            logger.info(f"Message reçu : {playlist_request}")

            # Extraire les informations nécessaires
            job_id = playlist_request.get('id')
            user_id = playlist_request.get('userId')
            data = playlist_request.get('data')
            keywords = data.get('tags')
            name = data.get('name')
            description = data.get('description')
            logger.info(f"Traitement de la playlist pour Job ID: {job_id}, User ID: {user_id}")
            logger.info(f"Keywords: {keywords}, Name: {name}, Description: {description}")

            # Vérifie si les champs obligatoires sont présents
            if not job_id or not user_id:
                raise ValueError("Les champs 'id' et 'userId' sont obligatoires dans le message.")

            # Générer la playlist
            playlist_end_job = PlaylistService.generate_playlist(
                keywords, name, description, job_id=job_id, user_id=user_id
            )

            if not playlist_end_job:
                logger.error("Échec de la génération de la playlist.")
                return

            stomp = controllers.stomp

            # Publier le résultat dans la queue cible
            stomp.send_message(
                "com.jamify.orchestrator.playlist-done",
                json.dumps(playlist_end_job)
            )

            logger.info(f"Message envoyé à la queue 'com.jamify.orchestrator.playlist-done': {playlist_end_job}")

        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage JSON pour le message : {message}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message : {e}")
