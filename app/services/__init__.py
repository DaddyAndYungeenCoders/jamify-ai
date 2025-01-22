#  Copyright (c) 2024, LAPETITTE Matthieu
#  Tous droits réservés.

from app import controllers
from .music_service import MusicService
from .playlist_service import PlaylistService

music = MusicService()


def startlistener():
    stomp = controllers.stomp
    stomp.add_subscriber('com.jamify.ai.tag-gen', music.listen)
    stomp.add_subscriber('com.jamify.ai.playlist-gen', PlaylistService.consume_and_publish)
    return None
