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
        # Détecter la langue avec langid
        lang, _ = langid.classify(text)
        return lang
    except Exception as e:
        return jsonify({"error": f"Langue non prise en charge. {str(e)}"}), 400

def translate_to_english(text, lang):
    """
    Traduit un texte dans la langue spécifiée vers l'anglais si nécessaire.
    Utilise Google Translate pour effectuer la traduction.
    """
    if lang != "en":
        # Traduire le mot-clé dans la langue anglaise si nécessaire
        translated = translator.translate(text, src=lang, dest="en")
        return translated.text
    return text

def find_synonyms(word):
    """
    Trouve les synonymes d'un mot en utilisant WordNet en anglais.
    """
    synonyms = set()
    
    # Recherche des synonymes uniquement en anglais
    for synset in wn.synsets(word, lang="eng"):
        for lemma in synset.lemmas("eng"):
            synonyms.add(lemma.name().lower())

    return synonyms

class PlaylistService:
    @staticmethod
    def generate_playlist(csv_file, keywords, number=None):
        """
        Génère une playlist basée sur un ou plusieurs mots-clés, en considérant tous les synonymes trouvés.
        """
        # Charger les données depuis le fichier CSV
        data = pd.read_csv(csv_file)
        tags = data[TAG_FIELD].dropna().unique()

        # Trouver les tags similaires pour chaque mot-clé
        similar_tags = set()
        for keyword in keywords:
            similar_tags.update(PlaylistService.find_similar_tags(keyword, tags))

        # Filtrer les musiques correspondant aux tags similaires (globalement)
        filtered_songs = data[data['tag'].isin(similar_tags)]

        # Limiter le nombre de musiques seulement après avoir collecté tous les résultats
        if number is not None:
            filtered_songs = filtered_songs.head(number)

        return filtered_songs.to_dict(orient='records')

    @staticmethod
    def find_similar_tags(user_input, tags):
        """
        Trouve des tags similaires au mot-clé utilisateur en utilisant SpaCy et WordNet (si disponible).
        """
        lang = detect_language(user_input)  # Détecter la langue du mot-clé
        print(f"Langue détectée pour '{user_input}': {lang}")

        synonyms = set()
        
        # Traduire l'entrée utilisateur en anglais
        translated_input = translate_to_english(user_input, lang)
        print(f"Mot-clé traduit en anglais : {translated_input}")

        # Trouver des synonymes en anglais
        synonyms.update(find_synonyms(translated_input))

        # Inclure le mot-clé lui-même dans les synonymes
        synonyms.add(translated_input.lower())
        print(f"Synonymes trouvés : {synonyms}")

        similar_tags = []
        # Comparer les synonymes aux tags
        for tag in tags:
            tag_doc = SPACY_MODEL(tag.lower())
            for synonym in synonyms:
                if synonym in tag_doc.text:
                    similar_tags.append(tag)
                    break

        return similar_tags
