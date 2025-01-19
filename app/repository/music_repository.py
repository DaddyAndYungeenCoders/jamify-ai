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


import psycopg2

from app.dto.music_dto import MusicDTO
from app.utils.logger import logger


class MusicRepository:
    def __init__(self, conn):
        self.conn = conn

    def add_music(self, music: MusicDTO):
        data = self.get_music_by_title(music.title)
        if isinstance(data, MusicDTO):
            return data.id
        sql = """INSERT INTO music(music_author,music_energy,music_image_src,music_isrc,music_tempo,music_title) VALUES(%s,%s,%s,%s,%s,%s) RETURNING music_id"""
        music_id = None

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (music.author, music.energy, music.imgurl, music.isrc, music.tempo, music.title,))
                rows = cur.fetchone()
                if rows:
                    music_id = rows[0]
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as e:
            logger.error(e)
        finally:
            return music_id
        pass

    def get_music_by_id(self, music_id):

        sql = """SELECT music_id, music_author, music_energy, music_image_src, music_isrc, music_tempo, music_title FROM music WHERE music_id = %s"""
        return self.private_get_music(sql, music_id)

    def get_music_by_title(self, title):
        sql = """SELECT music_id, music_author, music_energy, music_image_src, music_isrc, music_tempo, music_title FROM music WHERE music_title = %s"""
        return self.private_get_music(sql, title)

    def private_get_music(self, sql, selector):
        music = None
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (selector,))
                row = cur.fetchone()
                if row:
                    music = MusicDTO(
                        id=row[0],
                        author=row[1],
                        energy=row[2],
                        imgurl=row[3],
                        isrc=row[4],
                        tempo=row[5],
                        title=row[6]
                    )
        except (Exception, psycopg2.DatabaseError) as e:
            logger.error(e)
        finally:
            return music
