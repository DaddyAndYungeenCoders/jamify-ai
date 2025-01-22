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

from flask import Blueprint, request, jsonify

from app.controllers.stomp_controller import StompController
from app.services.playlist_service import PlaylistService

playlist_controller = Blueprint('playlist_controller', __name__)
stomp_controller = StompController()


@playlist_controller.route('/', methods=['POST'])
def generate_playlist():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Le corps de la requête est vide."}), 400

        # Validation des champs requis
        if 'id' not in data or 'userId' not in data or 'data' not in data:
            return jsonify({"error": "Les champs 'id', 'userId' et 'data' sont requis."}), 400

        job_id = data['id']
        user_id = data['userId']
        job_data = data['data']

        # Validation des données internes
        if 'tags' not in job_data or 'numberOfTitle' not in job_data:
            return jsonify({"error": "Les champs 'tags' et 'numberOfTitle' sont requis dans 'data'."}), 400

        tags = job_data['tags']
        number_of_titles = job_data['numberOfTitle']

        # Validation si 'tags' est une liste
        if not isinstance(tags, list):
            return jsonify({"error": "'tags' doit être une liste."}), 400

        # Suppression des espaces superflus autour de chaque tag
        keywords = [tag.strip() for tag in tags]

        if not isinstance(number_of_titles, int):
            return jsonify({"error": "'numberOfTitle' doit être un entier."}), 400

        # Appel au service de génération de playlist
        csv_file = "app/playlist/music_tags_realistic.csv"
        playlist_end_job = PlaylistService.generate_playlist(csv_file, keywords, number_of_titles, job_id, user_id)

        # Envoi de la réponse dans la queue STOMP
        destination = "/queue/playlist"  # Nom de la queue STOMP
        stomp_controller.send_message(destination, str(playlist_end_job))

        return jsonify({"message": "Playlist générée et envoyée dans la queue STOMP.", "playlist": playlist_end_job}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
