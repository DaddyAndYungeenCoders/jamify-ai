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
import gc
import os
from urllib.parse import urlparse

import pandas as pd
import requests
from requests import HTTPError

from app import controllers
from app.controllers.stomp_controller import StompMultipleSend
from app.utils.logger import logger


class DataService:
    download_folder = os.path.join(".", "downloads")
    stomp_controller = None

    def import_data(self, tagger_dto):
        self.stomp_controller = controllers.stomp
        csv_files = []
        os.makedirs(self.download_folder, exist_ok=True)
        # Télécharger et vérifier chaque fichier
        for dataset in tagger_dto:
            logger.info(dataset)
            file_path = self.download_data(dataset['url'])
            if file_path and self.is_csv(file_path):
                csv_files.append(CsvFile(file_path, dataset['spotid'], dataset['header']))
        df_data = self.merge_data(csv_files)
        self.send_music(df_data)
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
                pass
            logger.info(f"Fichier téléchargé : {file_path}")
            return file_path
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur de téléchargement du fichier {url} : {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de téléchargement du fichier {url} : {e}")
            return None

    @staticmethod
    def merge_data(csv_files):
        """Fusionne les fichiers CSV en optimisant la mémoire."""
        all_chunks = []
        logger.info("Start merging data")
        for csv_file in csv_files:
            chunks = pd.read_csv(csv_file.file_path, chunksize=10000,
                                 dtype={'spot_id': 'int32'})  # Optimisation type dès la lecture
            all_chunks.append(list(chunks))

        merged_chunks = []
        first_file_chunks = all_chunks[0]

        for i, file_chunks in enumerate(all_chunks[1:]):
            for chunk1 in first_file_chunks:
                for chunk2 in file_chunks:
                    chunk2 = chunk2.loc[:, ~chunk2.columns.duplicated()]
                    merged_chunk = pd.merge(chunk1, chunk2, left_on=csv_files[0].spot_id,
                                            right_on=csv_files[i + 1].spot_id, how='outer')
                    merged_chunks.append(merged_chunk)
                    del chunk2  # Supprime chunk2 explicitement après utilisation
                    gc.collect()  # Force le garbage collector
            first_file_chunks = merged_chunks
            merged_chunks = []
            gc.collect()

        final_df = pd.concat(first_file_chunks, ignore_index=True)
        logger.info("All data is merged")
        return final_df

    def send_music(self, merged_df):
        chunk_size = 500
        logger.info("Start send data to Active MQ")
        for start in range(0, len(merged_df), chunk_size):
            chunk = merged_df.iloc[start:start + chunk_size]
            commit = StompMultipleSend(self.stomp_controller.connection, "com.jamify.ai.tag-gen")
            for index, row in chunk.iterrows():  # itertuples est plus rapide que iterrows, mais pour la conversion json, il faut rester en iterrows
                commit.send(row.to_json())
            del commit, chunk
            gc.collect()
            logger.debug("data add to queue: %s", start + chunk_size)
        logger.info("All data is send to Active MQ")



class CsvFile:
    def __init__(self, file_path, spot_id, headers):
        self.file_path = file_path
        self.spot_id = spot_id
        self.headers = headers
