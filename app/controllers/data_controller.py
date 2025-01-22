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

from multiprocessing import Process

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.dto.dataset_dto import DatasetDTO
from app.services.data_service import DataService

data_controller = Blueprint('data_controller', __name__)


@data_controller.route('/', methods=['POST'])
def make_dataset():
    data = request.get_json()

    # Utilise le schéma de validation pour valider les données
    schema = DatasetDTO(many=True)

    try:
        # Valider les données
        validated_data = schema.load(data)
    except ValidationError as err:
        # Si validation échoue, retourner les erreurs avec un code 400
        return jsonify({"error": err.messages}), 400

    # Traitement des données validées
    dataset = []
    for item in validated_data:
        # Créer un DatasetDTO à partir des données validées
        dataset_dto = DatasetDTO().load(item)

        # Appeler le service pour effectuer la prédiction
        dataset.append(dataset_dto)
    heavy_process = Process(  # Create a daemonic process with heavy "my_func"
        target=DataService().import_data,
        args=(dataset,),
        daemon=True
    )
    heavy_process.start()

    return jsonify("ok"), 200  # Return 200 with OK
