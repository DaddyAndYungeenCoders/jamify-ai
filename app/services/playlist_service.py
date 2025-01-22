import os
import requests
import spacy
from googletrans import Translator
import pandas as pd
import langid
from flask import jsonify
from app.utils.constants import SPACY_MODEL_NAME, TAG_FIELD

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

def download_glove_vectors(base_url, target_dir, files):
    """
    Télécharge les fichiers nécessaires depuis un bucket S3.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    for file_name in files:
        file_url = f"{base_url}/{file_name}"
        local_file_path = os.path.join(target_dir, file_name.replace("/", os.sep))
        
        # Créer les sous-dossiers si nécessaire
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        if not os.path.exists(local_file_path):
            print(f"Téléchargement de {file_name}...")
            response = requests.get(file_url, stream=True)
            if response.status_code == 200:
                with open(local_file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                print(f"{file_name} téléchargé avec succès.")
            else:
                raise RuntimeError(f"Impossible de télécharger {file_name}. Erreur {response.status_code}.")
        else:
            print(f"{file_name} est déjà présent.")

# Télécharger tous les fichiers nécessaires
download_glove_vectors(S3_BASE_URL, SPACY_MODEL_DIR, GLOVE_VECTOR_FILES)

# Charger les vecteurs convertis dans SpaCy
SPACY_MODEL = spacy.load(SPACY_MODEL_DIR)

# Vérification du chargement des vecteurs
if not SPACY_MODEL("music").has_vector:
    raise RuntimeError("Les vecteurs GloVe ne sont pas chargés correctement.")
else:
    print("Les vecteurs GloVe sont bien chargés dans SpaCy.")

# Création du traducteur Google Translate
translator = Translator()

def detect_language(text):
    """
    Détecte la langue d'un texte avec langid.
    """
    try:
        lang, _ = langid.classify(text)
        return lang
    except Exception as e:
        raise ValueError(f"Langue non prise en charge : {str(e)}")

def translate_to_english(text, lang):
    """
    Traduit un texte vers l'anglais si nécessaire.
    """
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

        # Vérifier si le vecteur existe
        if not input_vector.has_vector:
            print(f"Le mot '{translated_input}' n'a pas de vecteur.")
            return []

        # Seuils de similarité
        seuils = [0.7, 0.6, 0.5]  # Teste plusieurs seuils pour plus de flexibilité

        for seuil in seuils:
            for tag in tags:
                # Nettoyer et découper les tags composés
                tag_words = tag.replace(" ", "").split(",")

                # Comparaison de chaque mot dans le tag
                for word in tag_words:
                    tag_vector = SPACY_MODEL(word.lower())

                    # Vérifier si le vecteur existe
                    if not tag_vector.has_vector:
                        continue

                    similarity = input_vector.similarity(tag_vector)

                    if similarity > seuil:
                        similar_tags.append(tag)
                        break  # Dès qu'un mot est similaire, passer au tag suivant

            # Si des tags sont trouvés, arrêter les tests
            if similar_tags:
                break

        print(f"Tags similaires trouvés : {similar_tags}")
        return similar_tags
