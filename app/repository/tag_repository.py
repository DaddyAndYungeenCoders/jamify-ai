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
import random as rand

from app.dto.music_tag_dto import MusicTagDTO
from app.dto.tag_dto import TagDTO
from app.utils.logger import logger


class TagRepository:
    def __init__(self, conn):
        self.conn = conn

    def private_get_tag(self, sql, selector):
        tag = None
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (selector,))
                row = cur.fetchone()
                if row:
                    tag = TagDTO(
                        id=row[0],
                        name=row[1]
                    )
        except (Exception, psycopg2.DatabaseError) as e:
            logger.error(e)
        finally:
            return tag

    def private_get_link_music_tag(self, sql, selector):
        tag = []
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (selector,))
                row = cur.fetchall()
                for r in row:
                    tag.append(MusicTagDTO(
                        music=r[0],
                        tag=r[1]))
        except (Exception, psycopg2.DatabaseError) as e:
            logger.error(e)
        finally:
            return tag

    def get_tag_by_id(self, tag_id):
        sql = """SELECT tag_id, tag_label FROM tag_entity WHERE tag_id = %s"""
        return self.private_get_tag(sql, tag_id)

    def get_tag_by_name(self, name: str) -> TagDTO:
        sql = """SELECT tag_id, tag_label FROM tag_entity WHERE tag_label = %s"""
        return self.private_get_tag(sql, name)

    def get_all_tags(self):
        sql = """SELECT tag_id, tag_label FROM tag_entity"""
        return self.private_get_tag(sql, "")

    def add_tag(self, label: str)-> TagDTO:
        sql = """INSERT INTO tag_entity(tag_label, tag_id) VALUES(%s, %s) RETURNING tag_id, tag_label"""
        tag_id = None
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (label,rand.randint(1, 1000000)))
                rows = cur.fetchone()
                if rows:
                    tag_id = TagDTO(
                        id=rows[0],
                        name=rows[1]
                    )
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as e:
            logger.error(e)
        finally:
            return tag_id

    def add_music_tag(self, music_id, tag_id):
        sql = """INSERT INTO music_tag(music_id, tag_id) VALUES(%s,%s)"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (music_id, tag_id,))
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as e:
            logger.error(e)

    def add_link_music_tag(self, music_id, tag_name):
        tag = self.get_tag_by_name(tag_name)
        if not tag:
            tag = self.add_tag(tag_name)
        self.add_music_tag(music_id, str(tag.id))
        pass

    def get_tag_by_music(self, music_id):
        sql = """SELECT music_id,tag_id FROM music_tag WHERE music_id = %s"""
        links = self.private_get_link_music_tag(sql, music_id)
        tags = []
        for link in links:
            tags.append(self.get_tag_by_id(link.tag_id).name)
        return tags
