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

from marshmallow import ValidationError

os.environ['TESTING'] = 'True'

from app.dto.queue_music_tag_dto import QueueMusicTagDTO


class TestQueueMusicTagDTO(unittest.TestCase):
    def setUp(self):
        # Créer l'instance mockée

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

    def test_reel_data(self):
        valid_data = {"id": None, "name": None, "album_name": None, "artists": None, "danceability": None,
                      "energy": None, "key": None, "loudness": None, "mode": None, "speechiness": None,
                      "acousticness": None, "instrumentalness": None, "liveness": None, "valence": None, "tempo": None,
                      "duration_ms_x": None, "lyrics": None, "track_id": "001BzmD9j45Cqa50xVNsQx",
                      "track_title": "Steam Valve", "duration_ms_y": 372970.0, "isrc": "DEAR41419075",
                      "track_number": 50.0, "release_id": "33ovXxjJnPq3PMDwJbagDp", "explicit": "f", "disc_number": 1.0,
                      "preview_url": "https:p.scdn.co/mp3-preview/"
                                     "5e52d2e4a893fc969ead35b0078c58867a48ed4e?cid=529623fe55c9470c9267eb399357c9d2",
                      "updated_on": "2023-08-22 18:10:52"}
        data_cleaned = self.schema.preprocess(valid_data)
        # Valider les données
        validated_data = self.schema.load(data_cleaned)
        dataset_dto = QueueMusicTagDTO().load(validated_data)
        print(dataset_dto)
        self.assertEqual(validated_data['name'], "Steam Valve")
        self.assertEqual(validated_data['track_number'], 50)
        self.assertEqual(validated_data['release_id'], "33ovXxjJnPq3PMDwJbagDp")
        self.assertEqual(validated_data['explicit'], False)
        self.assertEqual(validated_data['disc_number'], 1)


if __name__ == '__main__':
    unittest.main()
