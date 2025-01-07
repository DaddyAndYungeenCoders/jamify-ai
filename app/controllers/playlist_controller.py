from flask import Blueprint, request, jsonify
from app.services.playlist_service import PlaylistService
from app.utils.constants import JSON_FIELDS

playlist_controller = Blueprint('playlist_controller', __name__)

@playlist_controller.route('/', methods=['POST'])
def generate_playlist():
    try:
        data = request.get_json()
        if not data or JSON_FIELDS["KEYWORDS"] not in data:
            return jsonify({"error": "Le champ 'keywords' est requis dans le corps de la requête."}), 400

        keywords = data[JSON_FIELDS["KEYWORDS"]]
        number = data.get(JSON_FIELDS["NUMBER"], None)

        if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
            return jsonify({"error": "'keywords' doit être une liste de chaînes de caractères."}), 400

        csv_file = "app/playlist/music_tags_realistic.csv"
        playlist = PlaylistService.generate_playlist(csv_file, keywords, number)

        return jsonify(playlist), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
