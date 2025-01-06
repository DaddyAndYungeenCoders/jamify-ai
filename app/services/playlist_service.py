import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from spacy.language import Language
import pandas as pd

# Charger le modèle SpaCy
nlp = spacy.load('en_core_web_sm')

# Enregistrer WordnetAnnotator comme une factory Spacy
@Language.factory("wordnet_annotator")
def create_wordnet_annotator(nlp, name):
    return WordnetAnnotator(nlp, name=name)  # Fournir 'name' à WordnetAnnotator

# Ajouter WordnetAnnotator à la pipeline NLP en utilisant le nom du composant enregistré
nlp.add_pipe("wordnet_annotator", name="wordnet_annotator", last=True)

class PlaylistService:
    @staticmethod
    def generate_playlist(csv_file, user_input):
        """
        Génère une playlist basée sur un mot-clé.
        """
        # Charger les données depuis le fichier CSV
        data = pd.read_csv(csv_file)
        tags = data['tag'].dropna().unique()

        # Trouver les tags similaires
        similar_tags = PlaylistService.find_similar_tags(user_input, tags)
        print(f"tags : {similar_tags}")

        # Filtrer les musiques avec des tags similaires
        filtered_songs = data[data['tag'].isin(similar_tags)]
        return filtered_songs.to_dict(orient='records')

    def find_similar_tags(user_input, tags):
        """
        Trouve des tags similaires au mot-clé utilisateur en utilisant SpaCy et WordNet.
        """
        user_input_doc = nlp(user_input.lower())
        synonyms = set()

        # Ajouter les synonymes du mot-clé utilisateur
        for token in user_input_doc:
            print(f"Token: {token.text}")  # Afficher les tokens traités
            for synset in token._.wordnet.synsets():
                print(f"Synset: {synset}")  # Afficher le synset associé
                for lemma in synset.lemma_names():
                    print(f"Lemma: {lemma}")  # Afficher chaque synonyme
                    synonyms.add(lemma.lower())

                # Explorer les hypernyms et hyponymes
                for hypernym in synset.hypernyms():
                    for lemma in hypernym.lemma_names():
                        synonyms.add(lemma.lower())
                for hyponym in synset.hyponyms():
                    for lemma in hyponym.lemma_names():
                        synonyms.add(lemma.lower())

        # Inclure le mot-clé lui-même
        synonyms.add(user_input.lower())

        print(f"Synonyms found: {synonyms}")  # Afficher tous les synonymes trouvés

        similar_tags = []

        # Comparer les synonymes aux tags
        for tag in tags:
            tag_doc = nlp(tag.lower())
            for synonym in synonyms:
                if synonym in tag_doc.text:
                    similar_tags.append(tag)
                    break

        return similar_tags

