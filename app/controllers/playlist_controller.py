from flask import Blueprint, request, jsonify
from app.services.playlist_service import PlaylistService

playlist_controller = Blueprint('playlist_controller', __name__)

@playlist_controller.route('/<string:keyword>', methods=['GET'])
def generate_playlist(keyword):
    """
    Génère une playlist à partir du mot-clé fourni dans l'URL.
    """
    try:
        # Chemin du fichier CSV
        csv_file = "app/playlist/music_tags_realistic.csv"

        # Générer la playlist en utilisant le mot-clé passé dans l'URL
        playlist = PlaylistService.generate_playlist(csv_file, keyword)
        return jsonify(playlist), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
