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
import unittest

from marshmallow import ValidationError

from app.dto.queue_music_tag_dto import QueueMusicTagDTO


class TestQueueMusicTagDTO(unittest.TestCase):

    def setUp(self):
        self.schema = QueueMusicTagDTO()

    def test_valid_data(self):
        valid_data = {
            "id": "1",
            "name": "Song Title",
            "artists": "Artist Name",
            "duration": 300,
            "album_name": "Album Title",
            "isrc": "US1234567890",
            "track_number": 1,
            "release_id": "release_1",
            "explicit": True,
            "disc_number": 1,
            "preview_url": "http://example.com/preview",
            "danceability": 0.8,
            "energy": 0.7,
            "key": 5,
            "loudness": -5.0,
            "mode": 1,
            "speechiness": 0.05,
            "acousticness": 0.2,
            "instrumentalness": 0.0,
            "liveness": 0.1,
            "valence": 0.6,
            "tempo": 120.0,
            "duration_ms_x": 300000,
            "lyrics": "Some lyrics here"
        }
        result = self.schema.load(valid_data)
        self.assertEqual(result, valid_data)

    def test_missing_required_fields(self):
        invalid_data = {
            "name": "Song Title",
            "artists": "Artist Name"
            # 'id' is missing
        }
        with self.assertRaises(ValidationError) as context:
            self.schema.load(invalid_data)
        self.assertIn('id', str(context.exception.messages))

    def test_invalid_data_type(self):
        invalid_data = {
            "id": "1",
            "name": "Song Title",
            "artists": "Artist Name",
            "duration": "not an integer"  # Invalid type
        }
        with self.assertRaises(ValidationError) as context:
            self.schema.load(invalid_data)
        self.assertIn('duration', str(context.exception.messages))

    def test_optional_fields(self):
        valid_data = {
            "id": "1",
            "name": "Song Title",
            "artists": "Artist Name"
            # All optional fields are omitted
        }
        result = self.schema.load(valid_data)
        self.assertEqual(result['id'], "1")
        self.assertEqual(result['name'], "Song Title")
        self.assertEqual(result['artists'], "Artist Name")
        self.assertNotIn('duration', result)
        self.assertNotIn('album_name', result)


if __name__ == '__main__':
    unittest.main()
