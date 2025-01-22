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

import os
import zipfile
from typing import List, Dict, Tuple

import numpy as np
import requests
import transformers

from app.utils.logger import logger


class TagService:
    model_place = os.path.join(".", "models", "latest")
    # Définition des tags avec leurs plages de caractéristiques
    TAG_DEFINITIONS = {
        'Joyeux': {
            'valence': (0.7, 1.0),
            'danceability': (0.5, 0.9),
            'energy': (0.6, 0.9),
            'tempo': (100, 140)
        },
        'Triste': {
            'valence': (0.0, 0.3),
            'acousticness': (0.6, 1.0),
            'energy': (0.2, 0.5),
            'tempo': (50, 90)
        },
        'Énergique': {
            'energy': (0.8, 1.0),
            'danceability': (0.7, 1.0),
            'tempo': (120, 160),
            'loudness': (-10, 0)
        },
        'Relaxant': {
            'acousticness': (0.6, 1.0),
            'energy': (0.2, 0.5),
            'tempo': (60, 90),
            'valence': (0.4, 0.7)
        },
        'Romantique': {
            'valence': (0.5, 0.8),
            'tempo': (80, 110),
            'acousticness': (0.4, 0.7),
            'energy': (0.3, 0.6)
        },
        'Colérique': {
            'energy': (0.8, 1.0),
            'loudness': (-5, 0),
            'tempo': (120, 180),
            'danceability': (0.6, 0.9)
        },
        'Motivant': {
            'energy': (0.7, 1.0),
            'valence': (0.5, 0.8),
            'tempo': (100, 140),
            'danceability': (0.6, 0.9)
        },
        'Sombre': {
            'valence': (0.0, 0.3),
            'energy': (0.4, 0.7),
            'loudness': (-30, -10),
            'acousticness': (0.5, 1.0)
        },
        'Festif': {
            'danceability': (0.8, 1.0),
            'valence': (0.7, 1.0),
            'energy': (0.8, 1.0),
            'tempo': (120, 160)
        }
    }

    def __init__(self, tag_repository):
        """
        Initialise le générateur de tags

        :param tag_repository: Repository pour gérer les tags
        """
        self.tag_repository = tag_repository

    def _ensure_tags_exist(self):
        """
        Vérifie et crée les tags prédéfinis s'ils n'existent pas
        """
        for tag_name in self.TAG_DEFINITIONS.keys():
            existing_tag = self.tag_repository.get_tag_by_name(tag_name)
            if not existing_tag:
                self.tag_repository.add_tag(tag_name)

    def generate_tags(self, music_data) -> List[str]:
        """
        Génère les tags pour un morceau en fonction de ses caractéristiques

        :param music_data: Données musicales du morceau
        :return: Liste des tags correspondants
        """
        matching_tags = []

        for tag_name, tag_criteria in self.TAG_DEFINITIONS.items():
            if self._check_tag_match(music_data, tag_criteria):
                matching_tags.append(tag_name)

        elements = os.listdir(self.model_place)
        if len(elements) < 2:
            self._download_model()

        model_dir = self.model_place
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_dir)
        model = transformers.AutoModelForSequenceClassification.from_pretrained(model_dir)
        pipeline = transformers.pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)

        emotions = pipeline(music_data['lyrics'], truncation=True)[0]
        for emotion in emotions:
            if emotion['score'] > 0.8:
                matching_tags.append(emotion['label'])

        return matching_tags

    def _download_model(self):
        os.makedirs(self.model_place, exist_ok=True)
        nom_fichier_zip = os.path.join(self.model_place, 'fichier.zip')

        try:
            logger.debug("Début de téléchargement du model terminé.")
            response = requests.get("https://jamify.blob.core.windows.net/model/pytorch_model.zip")
            response.raise_for_status()  # Vérifie si la requête a réussi
            with open(nom_fichier_zip, 'wb') as f:
                f.write(response.content)
            logger.debug("Téléchargement du model terminé.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors du téléchargement : {e}")
            return

        # Extraire le fichier zip
        try:
            logger.debug(f"Extraction de {nom_fichier_zip}...")
            with zipfile.ZipFile(nom_fichier_zip, 'r') as zip_ref:
                zip_ref.extractall(self.model_place)
            logger.debug("Extraction terminée.")
        except zipfile.BadZipFile:
            logger.error("Erreur : le fichier téléchargé n'est pas un fichier zip valide.")
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction : {e}")
        pass

    def _check_tag_match(
            self,
            music_data,
            tag_criteria: Dict[str, Tuple[float, float]]
    ) -> bool:
        """
        Vérifie si les caractéristiques d'un morceau correspondent aux critères d'un tag

        :param music_data: Données musicales
        :param tag_criteria: Critères du tag
        :return: True si le morceau correspond au tag, False sinon
        """
        matches = []

        for feature, (min_val, max_val) in tag_criteria.items():
            # Vérifier si la caractéristique existe dans les données musicales
            if feature in music_data and music_data[feature] is not None:
                # Vérifier si la valeur est dans la plage du tag
                matches.append(min_val <= music_data[feature] <= max_val)

        # Le tag correspond si au moins la moitié des critères sont satisfaits
        return len(matches) > 0 and np.mean(matches) >= 0.5

    def tag_music(self, music_data, music_id):
        """
        Étiquette un morceau avec les tags correspondants

        :param music_data: Données musicales du morceau
        :param music_id: uuid of the music, generated by postgres
        """

        # Générer les tags
        try:
            tags = self.generate_tags(music_data)
        except Exception as e:
            logger.warning(e)
            return None
        # Ajouter les tags au morceau
        logger.info(f"Ajout des tags {tags} au morceau {music_id}")
        for tag in tags:
            try:
                self.tag_repository.add_link_music_tag(music_id, str(tag))
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout du tag {tag}: {e}")
