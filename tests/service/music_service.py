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

import os
import unittest
from unittest.mock import patch, MagicMock

from marshmallow import ValidationError

os.environ['TESTING'] = 'True'
from app.services.music_service import MusicService  # Adjust the import based on your project structure
from app.repository import Repository, MusicRepository, TagRepository


class TestMusicService(unittest.TestCase):

    def setUp(self):
        self.music_service = MusicService()
        self.repository_mock = MagicMock(spec=Repository)
        self.repository_mock.music_repository = MagicMock(spec=MusicRepository)
        self.repository_mock.tags_repository = MagicMock(spec=TagRepository)
        self.music_service.dataset_dto = {
            'name': 'Test Song',
            'artists': 'Test Artist',
            'isrc': 'US1234567890',
            'preview_url': 'http://example.com/image.jpg',
            'tempo': 120,
            'energy': 0.8,
            'lyrics': 'Test lyrics'
        }

    @patch('app.services.music_service.MusicDTO')
    def test_save_music(self, MockMusicDTO):
        # Arrange
        self.repository_mock.music_repository.add_music.return_value = 1  # Simulate returning a music ID

        # Act
        music_id = self.music_service.save_music(self.repository_mock)

        # Assert
        MockMusicDTO.assert_called_once_with(
            title='Test Song',
            author='Test Artist',
            isrc='US1234567890',
            imgurl='http://example.com/image.jpg',
            tempo='120',
            energy='0.8'
        )
        self.assertEqual(music_id, 1)

    @patch('app.services.music_service.TagService')
    def test_generate_tag(self, MockTagService):
        # Arrange
        music_id = 1
        tag_service_instance = MockTagService.return_value

        # Act
        self.music_service.generate_tag(self.repository_mock, music_id)

        # Assert
        tag_service_instance.tag_music.assert_called_once_with(self.music_service.dataset_dto, music_id)

    @patch('app.services.music_service.QueueMusicTagDTO')
    @patch('app.services.music_service.Repository')
    def test_listen_valid_data(self, MockRepository, MockQueueMusicTagDTO):
        # Arrange
        mock_queue_music_tag_dto_instance = MockQueueMusicTagDTO.return_value
        mock_queue_music_tag_dto_instance.load.return_value = self.music_service.dataset_dto
        mock_repository_instance = MockRepository.return_value
        mock_repository_instance.music_repository = MagicMock()
        mock_repository_instance.tags_repository = MagicMock()
        mock_repository_instance.music_repository.add_music.return_value = 1

        # Act
        result = self.music_service.listen('{'
                                           '"name": "Test Song", '
                                           '"artists": "Test Artist", '
                                           '"isrc": "US1234567890", '
                                           '"preview_url": "http://example.com/image.jpg", '
                                           '"tempo": 120, '
                                           '"energy": 0.8, '
                                           '"lyrics": "Test lyrics"'
                                           '}')

        # Assert
        self.assertTrue(result)
        mock_repository_instance.music_repository.add_music.assert_called_once()
        MockQueueMusicTagDTO.assert_called()

    @patch('app.services.music_service.QueueMusicTagDTO')
    def test_listen_invalid_data(self, MockQueueMusicTagDTO):
        # Arrange
        mock_queue_music_tag_dto_instance = MockQueueMusicTagDTO.return_value
        mock_queue_music_tag_dto_instance.load.side_effect = ValidationError("Invalid data")

        # Act
        with self.assertRaises(ValueError):
            self.music_service.listen('{"invalid": "data"}')

        # Assert
        # self.assertIsInstance(result, ValueError)


if __name__ == '__main__':
    unittest.main()
