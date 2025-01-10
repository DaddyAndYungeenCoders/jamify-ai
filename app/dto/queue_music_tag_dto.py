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
from datetime import datetime

from marshmallow import fields, Schema, post_load


class QueueMusicTagDTO(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    artists = fields.String(required=True)
    duration = fields.Integer(required=False, allow_none=True)
    album_name = fields.String(required=False, allow_none=True)
    isrc = fields.String(required=False, allow_none=True)
    track_number = fields.Integer(required=False, allow_none=True)
    release_id = fields.String(required=False, allow_none=True)
    explicit = fields.Boolean(required=False, allow_none=True)
    disc_number = fields.Integer(required=False, allow_none=True)
    preview_url = fields.String(required=False, allow_none=True)
    updated_on = fields.DateTime(required=False, allow_none=True)
    danceability = fields.Float(required=False, allow_none=True)
    energy = fields.Float(required=False, allow_none=True)
    key = fields.Integer(required=False, allow_none=True)
    loudness = fields.Float(required=False, allow_none=True)
    mode = fields.Integer(required=False, allow_none=True)
    speechiness = fields.Float(required=False, allow_none=True)
    acousticness = fields.Float(required=False, allow_none=True)
    instrumentalness = fields.Float(required=False, allow_none=True)
    liveness = fields.Float(required=False, allow_none=True)
    valence = fields.Float(required=False, allow_none=True)
    tempo = fields.Float(required=False, allow_none=True)
    duration_ms_x = fields.Integer(required=False, allow_none=True)
    lyrics = fields.String(required=False, allow_none=True)
    duration_ms_y = fields.Integer(required=False, allow_none=True)
    track_id = fields.String(required=False, allow_none=True)
    track_title = fields.String(required=False, allow_none=True)

    @post_load
    def convert_types(self, data, **kwargs):
        # Convertir 'updated_on' en chaîne de caractères si elle est présente
        if 'updated_on' in data and isinstance(data['updated_on'], datetime):
            data['updated_on'] = data['updated_on'].isoformat()  # Convertir en format ISO 8601

        if 'key' in data and isinstance(data['key'], str):
            data['key'] = int(data['key'])

        if 'mode' in data and isinstance(data['mode'], str):
            data['mode'] = int(data['mode'])

        return data
