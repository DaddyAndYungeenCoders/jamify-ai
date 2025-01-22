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
    def generate_playlist(csv_file, keywords, number=None, job_id=None, user_id=None):
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

        # Construction de la réponse
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": [{"idMusic": song['id']} for song in filtered_songs.to_dict(orient='records')]
        }

        return playlist_end_job

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
