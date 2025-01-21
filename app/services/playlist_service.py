import os
import requests
import spacy
from googletrans import Translator
import pandas as pd
import langid
from flask import jsonify
from nltk.corpus import wordnet as wn
from app.utils.constants import SPACY_MODEL_NAME, TAG_FIELD

# URL du bucket S3 contenant le modèle GloVe
GLOVE_URL = "https://jamifybucket.s3.eu-north-1.amazonaws.com/glove.840B.300d.txt"
GLOVE_DIR = "./glove"  # Répertoire local pour le modèle
GLOVE_FILE = os.path.join(GLOVE_DIR, "glove.840B.300d.txt")
SPACY_MODEL_DIR = "./glove_vectors"  # Répertoire pour les vecteurs SpaCy convertis

# Fonction pour télécharger le modèle GloVe
def download_glove_model(url, file_path):
    """
    Télécharge le fichier GloVe depuis un bucket S3 public si non présent localement.
    """
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        print(f"Téléchargement du modèle GloVe depuis {url}...")
        response = requests.get(url, stream=True)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Téléchargement terminé.")
    else:
        print("Modèle GloVe déjà téléchargé.")

# Fonction pour convertir GloVe en vecteurs SpaCy si nécessaire
def convert_glove_to_spacy(glove_file, spacy_model_dir):
    """
    Convertit les vecteurs GloVe en format SpaCy si nécessaire.
    """
    if not os.path.exists(spacy_model_dir):
        print("Les vecteurs GloVe ne sont pas convertis pour SpaCy.")
        print("Conversion des vecteurs GloVe en format SpaCy...")
        os.system(f"python -m spacy init vectors en {glove_file} {spacy_model_dir} --name glove")
        print("Conversion terminée.")
    else:
        print("Les vecteurs GloVe sont déjà convertis pour SpaCy.")

# Télécharger le modèle GloVe si nécessaire
download_glove_model(GLOVE_URL, GLOVE_FILE)

# Convertir GloVe en vecteurs SpaCy si nécessaire
convert_glove_to_spacy(GLOVE_FILE, SPACY_MODEL_DIR)

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
