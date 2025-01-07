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
import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import requests

from app.services.data_service import DataService, CsvFile


class TestDataService(unittest.TestCase):

    def setUp(self):
        self.data_service = DataService()
        self.test_url = "http://example.com/test.csv"
        self.test_spot_id = "spot123"
        self.test_header = ["header1", "header2"]
        self.test_csv_file_path = os.path.join(".", "downloads", "test.csv")

        # Créer un dossier de test pour les téléchargements
        os.makedirs(self.data_service.download_folder, exist_ok=True)

    @patch('app.controllers.stomp')
    @patch('app.utils.logger.logger')  # Assurez-vous que ce chemin est correct
    @patch('requests.get')
    def test_import_data_success(self, mock_requests_get, mock_logger, mock_stomp):
        # Simuler la réponse de la requête HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"header1,header2\nvalue1,value2"
        mock_requests_get.return_value = mock_response

        # Simuler la connexion STOMP
        mock_stomp.connected.return_value = None

        tagger_dto = [{'url': self.test_url, 'spotid': self.test_spot_id, 'header': self.test_header}]

        # Appel de la méthode
        self.data_service.import_data(tagger_dto)

        # Assertions
        mock_requests_get.assert_called_once_with(self.test_url)
        self.assertTrue(os.path.exists(self.test_csv_file_path))

        # Vérifier que le fichier CSV a été lu et fusionné
        merged_df = pd.read_csv(self.test_csv_file_path)
        self.assertEqual(merged_df.shape[0], 1)  # Vérifie qu'il y a une ligne dans le DataFrame

    @patch('app.utils.logger.logger')  # Assurez-vous que ce chemin est correct
    @patch('requests.get')
    def test_download_data_http_error(self, mock_requests_get, mock_logger):
        # Simuler une erreur HTTP
        mock_requests_get.side_effect = requests.exceptions.HTTPError("HTTP Error")

        result = self.data_service.download_data(self.test_url)

        # Assertions
        self.assertIsNone(result)

    @patch('app.utils.logger.logger')  # Assurez-vous que ce chemin est correct
    @patch('requests.get')
    def test_download_data_request_exception(self, mock_requests_get, mock_logger):
        # Simuler une exception de requête
        mock_requests_get.side_effect = requests.exceptions.RequestException("Request Error")

        result = self.data_service.download_data(self.test_url)

        # Assertions
        self.assertIsNone(result)

    def test_is_csv(self):
        self.assertTrue(self.data_service.is_csv("file.csv"))
        self.assertFalse(self.data_service.is_csv("file.txt"))

    @patch('pandas.read_csv')
    @patch('app.utils.logger.logger')  # Assurez-vous que ce chemin est correct
    def test_merge_data(self, mock_logger, mock_read_csv):
        # Simuler les fichiers CSV
        mock_read_csv.side_effect = [
            pd.DataFrame({'header1': ['value1'], 'header2': ['value2']}),
            pd.DataFrame({'spot123': ['value1'], 'header3': ['value3']})
        ]

        csv_files = [CsvFile("file1.csv", "header1", []), CsvFile("file2.csv", "spot123", [])]
        merged_df = self.data_service.merge_data(csv_files)

        # Assertions
        self.assertEqual(merged_df.shape[0], 1)  # Vérifie qu'il y a une ligne dans le DataFrame fusionné
        mock_read_csv.assert_any_call("file1.csv")
        mock_read_csv.assert_any_call("file2.csv")

    @patch('app.utils.logger.logger')  # Assurez-vous que ce chemin est correct
    @patch('requests.get')
    def test_send_music(self, mock_requests_get, mock_logger):
        # Simuler un DataFrame de musique
        df = pd.DataFrame({'music_id': [1], 'title': ['Test Song']})

        # Simuler la connexion STOMP
        self.data_service.stomp_controller = MagicMock()
        self.data_service.stomp_controller.connected.return_value = None

        # Appel de la méthode
        self.data_service.send_music(df)

        # Assertions
        self.data_service.stomp_controller.connected.assert_called_once()  # Vérifie que la connexion a été appelée


if __name__ == '__main__':
    unittest.main()