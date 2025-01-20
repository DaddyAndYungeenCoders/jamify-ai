import langid
from flask import jsonify
import spacy
from googletrans import Translator
from nltk.corpus import wordnet as wn
import pandas as pd
from app.utils.constants import SPACY_MODEL_NAME, TAG_FIELD

# Charger uniquement le modèle SpaCy en anglais
SPACY_MODEL = spacy.load(SPACY_MODEL_NAME)

# Créer un traducteur Google Translate
translator = Translator()

def detect_language(text):
    """
    Détecte la langue d'un texte, même si c'est un seul mot.
    Utilise langid pour la détection de langue.
    """
    try:
        lang, _ = langid.classify(text)
        return lang
    except Exception as e:
        raise ValueError(f"Langue non prise en charge : {str(e)}")

def translate_to_english(text, lang):
    """
    Traduit un texte dans la langue spécifiée vers l'anglais si nécessaire.
    """
    if lang != "en":
        translated = translator.translate(text, src=lang, dest="en")
        return translated.text
    return text

def find_synonyms(word):
    """
    Trouve les synonymes d'un mot en utilisant WordNet en anglais.
    """
    synonyms = set()
    for synset in wn.synsets(word, lang="eng"):
        for lemma in synset.lemmas("eng"):
            synonyms.add(lemma.name().lower())
    return synonyms

class PlaylistService:
    @staticmethod
    def generate_playlist(csv_file, keywords, number=None, job_id=None, user_id=None, name=None, description=None):
        """
        Génère une playlist basée sur des mots-clés et retourne un objet structuré avec les informations du job.
        """
        try:
            data = pd.read_csv(csv_file)
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement du fichier CSV : {str(e)}")

        tags = data[TAG_FIELD].dropna().unique()

        # Trouver les tags similaires pour chaque mot-clé
        similar_tags = set()
        for keyword in keywords:
            similar_tags.update(PlaylistService.find_similar_tags(keyword, tags))

        # Filtrer les musiques correspondant aux tags similaires
        filtered_songs = data[data[TAG_FIELD].isin(similar_tags)]

        # Limiter le nombre de musiques
        if number is not None:
            filtered_songs = filtered_songs.head(number)

        # Préparer la réponse structurée
        return {
            "id": job_id,
            "userId": user_id,
            "data": {
                "musics": [song['id'] for song in filtered_songs.to_dict(orient='records')],
                "name": name,
                "description": description
            }
        }

    @staticmethod
    def find_similar_tags(user_input, tags):
        """
        Trouve des tags similaires au mot-clé utilisateur en utilisant SpaCy et WordNet.
        """
        lang = detect_language(user_input)
        translated_input = translate_to_english(user_input, lang)
        synonyms = find_synonyms(translated_input)
        synonyms.add(translated_input.lower())
        print(synonyms)

        similar_tags = []
        for tag in tags:
            tag_doc = SPACY_MODEL(tag.lower())
            for synonym in synonyms:
                if synonym in tag_doc.text:
                    similar_tags.append(tag)
                    break

        return similar_tags
