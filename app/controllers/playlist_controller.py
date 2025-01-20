from flask import Blueprint, request, jsonify
from app.services.playlist_service import PlaylistService
from app.controllers.stomp_controller import StompController

playlist_controller = Blueprint('playlist_controller', __name__)
stomp_controller = StompController()

@playlist_controller.route('/', methods=['POST'])
def generate_playlist():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Le corps de la requête est vide."}), 400

        # Validation des champs requis
        required_fields = ['id', 'userId', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Le champ '{field}' est requis."}), 400

        job_id = data['id']
        user_id = data['userId']
        job_data = data['data']

        # Validation des champs dans 'data'
        required_data_fields = ['tags', 'name', 'description']
        for field in required_data_fields:
            if field not in job_data:
                return jsonify({"error": f"Le champ '{field}' est requis dans 'data'."}), 400

        # Récupérer et définir les valeurs
        tags = job_data['tags']
        name = job_data['name']
        description = job_data['description']

        # Si numberOfTitle n'est pas fourni, définir une valeur par défaut de 20
        number_of_titles = job_data.get('numberOfTitle', 20)

        # Validation des types de données
        if not isinstance(tags, list):
            return jsonify({"error": "'tags' doit être une liste."}), 400
        if not isinstance(number_of_titles, int):
            return jsonify({"error": "'numberOfTitle' doit être un entier."}), 400

        # Suppression des espaces superflus autour de chaque tag
        keywords = [tag.strip() for tag in tags]

        # Appel au service de génération de playlist
        csv_file = "app/playlist/music_tags_realistic.csv"
        playlist_end_job = PlaylistService.generate_playlist(
            csv_file,
            keywords,
            number_of_titles,
            job_id,
            user_id,
            name,
            description
        )

        # Envoi de la réponse dans la queue STOMP
        destination = "/queue/playlist"  # Nom de la queue STOMP
        stomp_controller.connected()
        stomp_controller.send_message(destination, str(playlist_end_job))

        return jsonify({"message": "Playlist générée et envoyée dans la queue STOMP.", "playlist": playlist_end_job}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

