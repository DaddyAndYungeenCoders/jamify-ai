import langid
from flask import jsonify
import spacy
from googletrans import Translator
import pandas as pd
from app.utils.constants import TAG_FIELD

# ✅ Chargement du modèle SpaCy avec les vecteurs GloVe
SPACY_MODEL = spacy.load("C:\\Users\\Jean-Baptiste\\Downloads\\GloVe-master\\glove_vecteurs_spacy")  # Chemin vers les vecteurs GloVe

# 🔍 Vérification du chargement des vecteurs
if not SPACY_MODEL("music").has_vector:
    print("⚠️ Les vecteurs GloVe ne sont pas chargés. Vérifie le chemin et le modèle.")
else:
    print("✅ Les vecteurs GloVe sont bien chargés dans SpaCy.")


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
        return jsonify({"error": f"Langue non prise en charge. {str(e)}"}), 400

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
    def generate_playlist(csv_file, keywords, number=None, job_id=None, user_id=None):
        """
        Génère une playlist basée sur la similarité des mots-clés avec les tags.
        """
        # 📥 Chargement des données CSV
        data = pd.read_csv(csv_file)
        tags = data[TAG_FIELD].dropna().unique()

        # 🔎 Recherche de tags similaires
        similar_tags = set()
        for keyword in keywords:
            similar_tags.update(PlaylistService.find_similar_tags(keyword, tags))

        # 🎵 Filtrer les musiques avec les tags similaires
        filtered_songs = data[data[TAG_FIELD].isin(similar_tags)]
        print(f"similar tag : {similar_tags}")

        # Limiter le nombre de musiques
        if number is not None:
            filtered_songs = filtered_songs.head(number)

        # 📦 Construire la réponse
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": [{"idMusic": song['id']} for song in filtered_songs.to_dict(orient='records')]
        }

        return playlist_end_job

    @staticmethod
    def find_similar_tags(user_input, tags):
        """
        Trouve des tags similaires au mot-clé en utilisant les vecteurs GloVe.
        """
        lang = detect_language(user_input)
        print(f"🌍 Langue détectée pour '{user_input}': {lang}")

        # 🔄 Traduction si nécessaire
        translated_input = translate_to_english(user_input, lang)
        print(f"🔤 Mot-clé traduit en anglais : {translated_input}")

        similar_tags = []
        input_vector = SPACY_MODEL(translated_input.lower())

        # ⚠️ Vérifier si le vecteur existe
        if not input_vector.has_vector:
            print(f"⚠️ Le mot '{translated_input}' n'a pas de vecteur.")
            return []

        # 📏 Seuils de similarité
        seuils = [0.7, 0.6, 0.5]  # Teste plusieurs seuils pour plus de flexibilité

        for seuil in seuils:
            for tag in tags:
                # 📝 Nettoyer et découper les tags composés
                tag_words = tag.replace(" ", "").split(",")
                
                # 🔎 Comparaison de chaque mot dans le tag
                for word in tag_words:
                    tag_vector = SPACY_MODEL(word.lower())

                    # Vérifier si le vecteur existe
                    if not tag_vector.has_vector:
                        continue

                    similarity = input_vector.similarity(tag_vector)

                    if similarity > seuil:
                        similar_tags.append(tag)
                        break  # Dès qu'un mot est similaire, passer au tag suivant

            # ✅ Si des tags sont trouvés, arrêter les tests
            if similar_tags:
                break

        print(f"🔗 Tags similaires trouvés : {similar_tags}")
        return similar_tags
