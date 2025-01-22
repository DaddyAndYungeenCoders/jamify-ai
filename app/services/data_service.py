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
from urllib.parse import urlparse

import pandas as pd
import requests
from requests import HTTPError

from app import controllers
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

        try:
            # Merge des fichiers
            df_data = self.merge_data(csv_files)

            # Envoi via STOMP
            self.send_music(df_data)

        except Exception as e:
            logger.error(f"Processing error: {e}")

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
    def merge_data(csv_files, chunk_size: int = 50000) -> pd.DataFrame:
        """Fusionne les fichiers CSV en optimisant la mémoire."""

        try:
            # Chargement des chunks
            df1_chunks = pd.read_csv(csv_files[0].file_path)
            df2_chunks = pd.read_csv(csv_files[1].file_path)

            merged_dataframes = []

            # for chunk1, chunk2 in zip(df1_chunks, df2_chunks):
            # Merge des chunks
            merged_chunk = pd.merge(
                df1_chunks,
                df2_chunks,
                left_on=csv_files[0].spot_id,
                right_on=csv_files[1].spot_id,
                how='left'
            )
            merged_dataframes.append(merged_chunk)

            # Concaténation finale
            final_merged_df = pd.concat(merged_dataframes, ignore_index=True)

            logger.info(f"Merge completed. Total rows: {len(final_merged_df)}")
            return final_merged_df

        except Exception as e:
            logger.error(f"Merge error: {e}")
            raise

    def send_music(self, merged_df):
        """
        Envoi des données via STOMP avec commit

        :param merged_df: DataFrame mergé à envoyer
        """
        try:
            # commit = StompMultipleSend(self.stomp_controller.connection, "com.jamify.ai.tag-gen")

            # Envoi ligne par ligne
            with self.stomp_controller.create_transaction("com.jamify.ai.tag-gen") as transaction:
                for _, row in merged_df.iterrows():
                    transaction.send(row.to_json())
                    # commit.send(row.to_json())
                    # self.stomp_controller.send_message("com.jamify.ai.tag-gen",row.to_json())
                    pass

            # Commit de la transaction
            # del commit
            logger.info("All messages sent and committed successfully")

        except Exception as e:
            logger.error(f"STOMP send error: {e}")


class CsvFile:
    def __init__(self, file_path, spot_id, headers):
        self.file_path = file_path
        self.spot_id = spot_id
        self.headers = headers
