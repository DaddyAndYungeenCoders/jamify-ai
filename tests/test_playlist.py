import unittest
from unittest.mock import patch
import pandas as pd
from app.services.playlist_service import PlaylistService
import nltk
nltk.download('wordnet')

class TestPlaylistService(unittest.TestCase):

    @patch('app.services.playlist_service.pd.read_csv')
    def test_generate_playlist(self, mock_read_csv):
        # Données simulées pour le test
        mock_data = pd.DataFrame({
            'id': [1, 2, 3],
            'tag': ['happy', 'sad', 'content'],
            'title': ['Song 1', 'Song 2', 'Song 3']
        })
        mock_read_csv.return_value = mock_data

        # Paramètres de test
        csv_file = "app/playlist/music_tags_realistic.csv"
        keywords = ['happy']
        number_of_titles = 2
        job_id = 1
        user_id = 123

        # Appel de la méthode à tester
        result = PlaylistService.generate_playlist(csv_file, keywords, number_of_titles, job_id, user_id)

        # Construction de la réponse attendue
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": [
                {"idMusic": 1},
            ]
        }

        # Assertions pour vérifier le comportement attendu
        self.assertEqual(result, playlist_end_job)

    @patch('app.services.playlist_service.pd.read_csv')
    def test_generate_playlist_no_results(self, mock_read_csv):
        # Données simulées pour le test
        mock_data = pd.DataFrame({
            'id': [1, 2, 3],
            'tag': ['sad', 'angry', 'disappointed'],
            'title': ['Song 1', 'Song 2', 'Song 3']
        })
        mock_read_csv.return_value = mock_data

        # Paramètres de test
        csv_file = "app/playlist/music_tags_realistic.csv"
        keywords = ['happy']
        number_of_titles = 2
        job_id = 1
        user_id = 123

        # Appel de la méthode à tester avec un mot-clé qui ne correspond à aucun tag
        result = PlaylistService.generate_playlist(csv_file, keywords, number_of_titles, job_id, user_id)

        # Construction de la réponse attendue
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": []
        }

        # Assertions pour vérifier le comportement attendu
        self.assertEqual(result, playlist_end_job)
