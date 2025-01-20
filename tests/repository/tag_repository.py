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
from unittest.mock import MagicMock

os.environ['TESTING'] = 'True'

from app.repository.tag_repository import TagRepository


class TestTagRepository(unittest.TestCase):

    def setUp(self):
        # Création d'une connexion simulée
        self.mock_conn = MagicMock()
        self.tag_repo = TagRepository(self.mock_conn)

    def test_get_tag_by_id_success(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (1, "TagName")

        # Appel de la méthode
        tag = self.tag_repo.get_tag_by_id(1)

        # Assertions
        self.assertIsNotNone(tag)
        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.name, "TagName")

    def test_get_tag_by_id_not_found(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

        # Appel de la méthode
        tag = self.tag_repo.get_tag_by_id(1)

        # Assertions
        self.assertIsNone(tag)

    def test_get_tag_by_name_success(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (1, "TagName")

        # Appel de la méthode
        tag = self.tag_repo.get_tag_by_name("TagName")

        # Assertions
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, "TagName")

    def test_get_tag_by_name_not_found(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = None

        # Appel de la méthode
        tag = self.tag_repo.get_tag_by_name("TagName")

        # Assertions
        self.assertIsNone(tag)

    def test_add_tag_success(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (
        1, "Test",)  # Simule un ID retourné

        # Appel de la méthode
        tag = self.tag_repo.add_tag("NewTag")

        # Assertions
        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.name, "Test")
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_add_tag_failure(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.side_effect = Exception("Database error")

        # Appel de la méthode
        tag_id = self.tag_repo.add_tag("NewTag")

        # Assertions
        self.assertIsNone(tag_id)
        self.mock_conn.commit.assert_not_called()

    def test_add_music_tag(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.return_value = None  # Simule l'insertion réussie
        self.tag_repo.add_music_tag(1, 1)

        # Assertions
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            """INSERT INTO music_tag(music_id, tag_id) VALUES(%s,%s)""", (1, 1)
        )
        self.mock_conn.commit.assert_called_once()

    def test_add_link_music_tag_new_tag(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.side_effect = [None, (
        1, "NewTag",)]  # Tag non trouvé
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.return_value = (
        1,)  # Simule l'insertion réussie

        # Appel de la méthode
        self.tag_repo.add_link_music_tag(1, "NewTag")

        # Assertions
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.assert_any_call(
            """INSERT INTO tag_entity(tag_label) VALUES(%s) RETURNING tag_id, tag_label""", ("NewTag",)
        )
        self.mock_conn.cursor.return_value.__enter__.return_value.execute.assert_any_call(
            """INSERT INTO music_tag(music_id, tag_id) VALUES(%s,%s)""", (1, 1)
        )
        self.mock_conn.commit.assert_called()

    def test_get_tag_by_music(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = [(1, 1)]
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchone.return_value = (1, "TagName")

        # Appel de la méthode
        tags = self.tag_repo.get_tag_by_music(1)

        # Assertions
        self.assertEqual(tags, ["TagName"])

    def test_get_tag_by_music_no_tags(self):
        # Préparation des données de test
        self.mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = []

        # Appel de la méthode
        tags = self.tag_repo.get_tag_by_music(1)

        # Assertions
        self.assertEqual(tags, [])


if __name__ == '__main__':
    unittest.main()
