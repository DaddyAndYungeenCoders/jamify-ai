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

import os
from urllib.parse import urlparse

import requests
from requests import HTTPError

from app.utils.logger import logger


class DataService:
    download_folder = os.path.join(".", "downloads")

    def import_data(self, tagger_dto):
        csv_files = []
        os.makedirs(self.download_folder, exist_ok=True)
        # Télécharger et vérifier chaque fichier
        for dataset in tagger_dto:
            logger.info(dataset)
            file_path = self.download_data(dataset['url'])
            if file_path and self.is_csv(file_path):
                csv_files.append(file_path)
        logger.info(csv_files)
        pass

    @staticmethod
    def is_csv(file_path):
        return file_path.endswith(".csv")

    def download_data(self, url):
        # Télécharge le fichier à partir de l'URL et sauvegarde dans le dossier spécifié
        try:
            # Effectuer la requête HTTP pour obtenir le contenu du fichier
            response = requests.get(url)
            response.raise_for_status()  # Lève une exception si la requête échoue
            if response.status_code != 200:
                raise HTTPError
            # Extraire le nom du fichier à partir de l'URL
            file_name = os.path.basename(urlparse(url).path)
            file_path = os.path.join(self.download_folder, file_name)

            # Sauvegarder le fichier téléchargé
            with open(file_path, 'wb') as file:
                file.write(response.content)
            logger.info(f"Fichier téléchargé : {file_path}")
            return file_path
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur de téléchargement du fichier {url} : {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de téléchargement du fichier {url} : {e}")
            return None
