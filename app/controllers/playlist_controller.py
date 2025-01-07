from flask import Blueprint, request, jsonify
from app.services.playlist_service import PlaylistService

# Créer le Blueprint pour le contrôleur Playlist
playlist_controller = Blueprint('playlist_controller', __name__)

@playlist_controller.route('/<string:keyword>', methods=['GET'])
def generate_playlist(keyword):
    """
    Génère une playlist à partir d'un ou plusieurs mots-clés fournis dans l'URL.
    """
    try:
        # Récupérer un éventuel paramètre 'number' pour la quantité de musique désirée
        number = request.args.get('number', default=None, type=int)

        # Récupérer les mots-clés, les diviser s'ils sont séparés par une virgule
        keywords = keyword.split(',')

        # Chemin du fichier CSV
        csv_file = "app/playlist/music_tags_realistic.csv"

        # Générer la playlist en utilisant les mots-clés passés dans l'URL
        playlist = PlaylistService.generate_playlist(csv_file, keywords, number)

        return jsonify(playlist), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
