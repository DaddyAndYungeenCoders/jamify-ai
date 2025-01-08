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
import unittest
from unittest.mock import MagicMock

from app.dto.music_dto import MusicDTO
from app.repository.music_repository import MusicRepository


class TestMusicRepository(unittest.TestCase):

    def setUp(self):
        # Création d'une connexion simulée
        self.mock_conn = MagicMock()
        self.music_repo = MusicRepository(self.mock_conn)

    def test_add_music_success(self):
        # Préparation des données de test
        music_dto = MusicDTO(author="Author", energy=5, imgurl="image_url", isrc="ISRC123", tempo=120, title="Title")
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (1,)  # Simule un ID retourné

        # Appel de la méthode
        music_id = self.music_repo.add_music(music_dto)

        # Assertions
        self.assertEqual(music_id, 1)
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_add_music_failure(self):
        # Préparation des données de test
        music_dto = MusicDTO(author="Author", energy=5, imgurl="image_url", isrc="ISRC123", tempo=120, title="Title")
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.side_effect = Exception("Database error")

        # Appel de la méthode
        music_id = self.music_repo.add_music(music_dto)

        # Assertions
        self.assertIsNone(music_id)
        self.mock_conn.commit.assert_not_called()

    def test_get_music_by_id_success(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (
            1, "Author", 5, "image_url", "ISRC123", 120, "Title")

        # Appel de la méthode
        music = self.music_repo.get_music_by_id(1)

        # Assertions
        self.assertIsNotNone(music)
        self.assertEqual(music.id, 1)
        self.assertEqual(music.author, "Author")

    def test_get_music_by_id_not_found(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

        # Appel de la méthode
        music_getted = self.music_repo.get_music_by_id(1)

        # Assertions
        self.assertIsNone(music_getted)

    def test_get_music_by_title_success(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (
            1, "Author", 5, "image_url", "ISRC123", 120, "Title")

        # Appel de la méthode
        music = self.music_repo.get_music_by_title("Title")

        # Assertions
        self.assertIsNotNone(music)
        self.assertEqual(music.title, "Title")

    def test_get_music_by_title_not_found(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

        # Appel de la méthode
        music_getted = self.music_repo.get_music_by_title("Title")

        # Assertions
        self.assertIsNone(music_getted)


if __name__ == '__main__':
    unittest.main()
