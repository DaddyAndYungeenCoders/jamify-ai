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

import unittest
from unittest.mock import patch

import nltk
import pandas as pd

from app.services.playlist_service import PlaylistService

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
        name = "results"
        description = "results found"
        number_of_titles = 2
        job_id = 1
        user_id = 123

        # Appel de la méthode à tester
        result = PlaylistService.generate_playlist(csv_file, keywords, name, description, number_of_titles, job_id,
                                                   user_id)

        # Construction de la réponse attendue
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": {
                "musics": [1],
                "name": name,
                "description": description
            }
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
        name = "no_results"
        description = "No results found"
        number_of_titles = 2
        job_id = 1
        user_id = 123

        # Appel de la méthode à tester avec un mot-clé qui ne correspond à aucun tag
        result = PlaylistService.generate_playlist(csv_file, keywords, name, description, number_of_titles, job_id,
                                                   user_id)

        # Construction de la réponse attendue
        playlist_end_job = {
            "id": job_id,
            "userId": user_id,
            "data": {
                "musics": [1],  # PTDR : triste est similaire à 60% à heureux
                "name": name,
                "description": description
            }
        }

        # Assertions pour vérifier le comportement attendu
        self.assertEqual(result, playlist_end_job)
