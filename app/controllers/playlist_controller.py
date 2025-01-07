from flask import Blueprint, request, jsonify
from app.services.playlist_service import PlaylistService

# Créer le Blueprint pour le contrôleur Playlist
playlist_controller = Blueprint('playlist_controller', __name__)

@playlist_controller.route('/', methods=['POST'])
def generate_playlist():
    """
    Génère une playlist à partir d'un ou plusieurs mots-clés fournis dans le corps de la requête JSON.
    """
    try:
        # Récupérer les données JSON envoyées dans le corps de la requête
        data = request.get_json()
        if not data or 'keywords' not in data:
            return jsonify({"error": "Le champ 'keywords' est requis dans le corps de la requête."}), 400

        # Extraire les mots-clés et le nombre facultatif de musiques
        keywords = data['keywords']  # Liste de mots-clés
        number = data.get('number', None)  # Nombre facultatif de musiques
        if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
            return jsonify({"error": "'keywords' doit être une liste de chaînes de caractères."}), 400

        # Chemin du fichier CSV
        csv_file = "app/playlist/music_tags_realistic.csv"

        # Générer la playlist en utilisant les mots-clés fournis
        playlist = PlaylistService.generate_playlist(csv_file, keywords, number)

        return jsonify(playlist), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
