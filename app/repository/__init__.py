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

import psycopg2

from app.utils.logger import logger
from .music_repository import MusicRepository
from .tag_repository import TagRepository


class Repository:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.music_repository = None
        self.tags_repository = None

    def connect(self, host=os.environ.get('DBHOST'), database=os.environ.get('DBNAME'), user=os.environ.get('DBUSER'),
                password=os.environ.get('DBPASS')):
        """ Connect to the PostgreSQL database server """
        pg_connection_dict = {
            'dbname': database,
            'user': user,
            'password': password,
            'port': 5432,
            'host': host
        }
        logger.debug("Connecting to Postgre with : %s", pg_connection_dict)
        try:
            # connecting to the PostgreSQL server
            with psycopg2.connect(**pg_connection_dict) as conn:
                logger.info('Connected to the PostgreSQL server.')
                self.connection = conn
            self.music_repository = MusicRepository(self.connection)
            self.tags_repository = TagRepository(self.connection)
        except (psycopg2.DatabaseError, Exception) as error:
            logger.error(error)

    def disconnect(self):
        """ Disconnect from the PostgreSQL database server """
        if self.connection:
            self.connection.close()
            logger.info('Database connection closed.')
