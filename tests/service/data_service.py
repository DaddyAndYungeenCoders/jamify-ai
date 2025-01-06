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
import os.path
import unittest
from unittest.mock import patch, MagicMock

import requests

from app.services.data_service import DataService


class DataServiceTest(unittest.TestCase):
    def test_isCsv_valid(self):
        result = DataService.is_csv("folder.csv")
        self.assertEqual(True, result)  # add assertion here

    def test_isCsv_wrong(self):
        result = DataService.is_csv("folder.xml")
        self.assertEqual(False, result)  # add assertion here

    @patch('requests.get')  # Mock de requests.get
    @patch('builtins.open', new_callable=unittest.mock.mock_open)  # Mock de open
    def test_download_data_success(self, mock_open, mock_get):
        # Configuration du mock pour requests.get
        url = "https://example.com/file.csv"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        mock_get.return_value = mock_response

        # Création d'une instance de DataDownloader
        data = DataService()
        # Appel de la méthode
        file_path = data.download_data(url=url)

        # Vérifications
        self.assertEqual(file_path, os.path.join(".", "downloads", "file.csv"))
        mock_get.assert_called_once_with(url)  # Vérifier que requests.get a été appelé une seule fois
        mock_open.assert_called_once_with(os.path.join(".", "downloads", "file.csv"),
                                          'wb')  # Vérifier que open a été appelé avec le bon chemin
        mock_open().write.assert_called_once_with(
            b"file content")  # Vérifier que le contenu a été écrit dans le fichier

    @patch('requests.get')  # Mock de requests.get
    @patch('builtins.open', new_callable=unittest.mock.mock_open)  # Mock de open
    def test_download_data_http_error(self, mock_open, mock_get):
        # Configuration du mock pour simuler une erreur HTTP (par exemple, 404)
        url = "https://example.com/file_not_found.csv"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Création d'une instance de DataDownloader
        data = DataService()
        # Appel de la méthode
        file_path = data.download_data(url=url)

        # Vérifications
        self.assertIsNone(file_path)  # La méthode doit retourner None en cas d'erreur HTTP
        mock_get.assert_called_once_with(url)  # Vérifier que requests.get a été appelé une seule fois
        mock_open.assert_not_called()  # open ne doit pas être appelé si le téléchargement échoue

    @patch('requests.get')  # Mock de requests.get
    @patch('builtins.open', new_callable=unittest.mock.mock_open)  # Mock de open
    def test_download_data_request_exception(self, mock_open, mock_get):
        # Configuration du mock pour simuler une exception de requête (par exemple, Timeout)
        url = "https://example.com/file.txt"
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Création d'une instance de DataDownloader
        data = DataService()

        # Appel de la méthode
        file_path = data.download_data(url=url)

        # Vérifications
        self.assertIsNone(file_path)  # La méthode doit retourner None en cas d'exception de requête
        mock_get.assert_called_once_with(url)  # Vérifier que requests.get a été appelé une seule fois
        mock_open.assert_not_called()  # open ne doit pas être appelé si une exception est levée

    @patch('os.makedirs')  # Mock de os.makedirs
    @patch('app.services.data_service.DataService.download_data')  # Mock de download_data
    @patch('app.services.data_service.DataService.is_csv')  # Mock de is_csv
    def test_import_data_success(self, mock_is_csv, mock_download_data, mock_makedirs):
        # Configuration des mocks
        tagger_dto = [
            {"url": "https://example.com/file1.csv"},
            {"url": "https://example.com/file2.csv"}
        ]
        mock_download_data.return_value = "./downloads/file1.csv"
        mock_is_csv.return_value = True

        # Création d'une instance de DataImporter
        data = DataService()

        # Appel de la méthode import_data
        data.import_data(tagger_dto)

        # Vérifications
        mock_makedirs.assert_called_once_with(data.download_folder, exist_ok=True)  # Vérifier que le dossier a été créé
        mock_download_data.assert_any_call("https://example.com/file2.csv")
        mock_download_data.assert_any_call(
            "https://example.com/file1.csv")  # Vérifier que download_data est appelé pour chaque fichier
        mock_is_csv.assert_any_call("./downloads/file1.csv")  # Vérifier que is_csv est appelé pour chaque fichier

    @patch('os.makedirs')  # Mock de os.makedirs
    @patch('app.services.data_service.DataService.download_data')  # Mock de download_data
    @patch('app.services.data_service.DataService.is_csv')  # Mock de is_csv
    def test_import_data_with_non_csv_files(self, mock_is_csv, mock_download_data, mock_makedirs):
        # Configuration des mocks
        tagger_dto = [
            {"url": "https://example.com/file1.csv"},
            {"url": "https://example.com/file2.txt"}  # Non-CSV
        ]
        mock_download_data.side_effect = [
            "/mock/folder/file1.csv",  # Téléchargement du fichier CSV
            "/mock/folder/file2.txt"  # Téléchargement d'un fichier non CSV
        ]
        mock_is_csv.side_effect = [True, False]  # Le premier fichier est un CSV, le second non

        # Création d'une instance de DataImporter
        data = DataService()

        # Appel de la méthode import_data
        data.import_data(tagger_dto)

        # Vérifications
        mock_makedirs.assert_called_once_with(data.download_folder, exist_ok=True)  # Vérifier que le dossier a été créé
        mock_download_data.assert_any_call("https://example.com/file1.csv")
        mock_download_data.assert_any_call("https://example.com/file2.txt")
        mock_is_csv.assert_any_call("/mock/folder/file1.csv")
        mock_is_csv.assert_any_call("/mock/folder/file2.txt")
        # Vérifier que seul le fichier CSV est ajouté à csv_files

    @patch('os.makedirs')  # Mock de os.makedirs
    @patch('app.services.data_service.DataService.download_data')  # Mock de download_data
    @patch('app.services.data_service.DataService.is_csv')  # Mock de is_csv
    def test_import_data_with_failed_download(self, mock_is_csv, mock_download_data, mock_makedirs):
        # Configuration des mocks pour simuler un échec du téléchargement
        tagger_dto = [{"url": "https://example.com/file1.csv"}]
        mock_download_data.return_value = None  # Simule un téléchargement échoué
        mock_is_csv.return_value = True  # Même si le fichier était un CSV, il n'a pas été téléchargé

        # Création d'une instance de DataImporter
        data = DataService()

        # Appel de la méthode import_data
        data.import_data(tagger_dto)

        # Vérifications
        mock_makedirs.assert_called_once_with(data.download_folder, exist_ok=True)  # Vérifier que le dossier a été créé
        mock_download_data.assert_called_with("https://example.com/file1.csv")  # Vérifier que download_data est appelé
        mock_is_csv.assert_not_called()  # is_csv ne doit pas être appelé si le téléchargement a échoué
        # Vérifier que csv_files reste vide


if __name__ == '__main__':
    unittest.main()
