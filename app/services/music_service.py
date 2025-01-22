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

import json

from marshmallow import ValidationError

from app.dto.music_dto import MusicDTO
from app.dto.queue_music_tag_dto import QueueMusicTagDTO
from app.repository import Repository
from app.services.tag_service import TagService
from app.utils.logger import logger


class MusicService:
    dataset_dto = None

    def __init__(self):
        pass

    def save_music(self, repository: Repository):
        # Convert Queue music DTO to the MusicDTO
        # logger.debug(self.dataset_dto)
        music = MusicDTO(
            title=self.dataset_dto['name'],
            author=self.dataset_dto['artists'],
            isrc=self.dataset_dto['isrc'],
            imgurl=self.dataset_dto['preview_url'],
            tempo=str(self.dataset_dto['tempo']),
            energy=str(self.dataset_dto['energy']),
        )

        return repository.music_repository.add_music(music)

    def generate_tag(self, repository: Repository, music_id):
        # Créer le générateur de tags
        tag_generator = TagService(repository.tags_repository)

        if self.dataset_dto['lyrics'] is not None:
            # Générer et ajouter les tags
            tag_generator.tag_music(self.dataset_dto, music_id)

        pass

    def listen(self, data):
        # Utilise le schéma de validation pour valider les données
        schema = QueueMusicTagDTO()
        try:
            data_cleaned = schema.preprocess(json.loads(data))
            # Valider les données
            validated_data = schema.load(data_cleaned)
        except ValidationError as err:
            logger.warning("data received : %s", data)
            logger.warning("Data not valid: %s", json.dumps(err.messages))
            logger.warning("Valid data : %s", json.dumps(err.valid_data))
            raise ValueError

        self.dataset_dto = QueueMusicTagDTO().load(validated_data)

        # Traitement des données validées
        # Save music in database
        database = Repository()
        database.connect()
        if not database.music_repository:
            logger.error("FAILED TO CONNECT TO DATABASE, FAILED TO SAVE MUSIC")
            return None
        if not database.tags_repository:
            logger.error("FAILED TO CONNECT TO DATABASE, FAILED TO SAVE TAGS")
            return None
        music_id = self.save_music(database)
        self.generate_tag(database, music_id)
        database.disconnect()

        return True
        pass
