#  Copyright (c) 2024, LAPETITTE Matthieu
#  Tous droits réservés.
#
#  Ce fichier est soumis aux termes de la licence suivante :
#  Vous êtes autorisé à utiliser, modifier et distribuer ce code sous réserve des conditions de la licence.
#  Vous ne pouvez pas utiliser ce code à des fins commerciales sans autorisation préalable.
#
#  Ce fichier est fourni "tel quel", sans garantie d'aucune sorte, expresse ou implicite, y compris mais sans s'y limiter,
#  les garanties implicites de qualité marchande ou d'adaptation à un usage particulier.
#
#  Pour toute question ou demande d'autorisation, contactez LAPETITTE Matthieu à l'adresse suivante :
#  matthieu@lapetitte.fr

# constants.py

# Champs JSON attendus dans la requête
JSON_FIELDS = {
    "KEYWORDS": "keywords",  # Liste des mots-clés
    "NUMBER": "number"       # Nombre facultatif de musiques
}

# Configuration du modèle SpaCy
SPACY_MODEL_NAME = "en_core_web_sm"
TAG_FIELD = "tag"
