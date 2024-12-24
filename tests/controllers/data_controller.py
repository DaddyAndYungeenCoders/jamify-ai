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

from unittest import TestCase
from unittest.mock import patch

from flask import Flask

from app.controllers.data_controller import data_controller

# On crée une application Flask pour tester
app = Flask(__name__)
app.register_blueprint(data_controller)


class TestDataController(TestCase):

    @patch('app.services.data_service.DataService.import_data')
    def test_make_dataset_success(self, mock_import_data):
        # Exemple de données valides
        valid_data = [
            {"url": "https://prout.fr/", "spotid": "csv", "header": ["source1", "srouce3"]},
            {"url": "http://prout.fr/", "spotid": "json", "header": ["source2", "srouce3"]}
        ]

        # Envoyer la requête POST
        with app.test_client() as client:
            response = client.post('/', json=valid_data)
            print(response.json)
            # Vérifier que la réponse a un statut 200
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, "ok")
            # Vérifier que le service d'importation a été appelé
            mock_import_data.assert_called_once()

    def test_make_dataset_invalid_data(self):
        # Exemple de données invalides (manque de champ "type")
        invalid_data = [
            {"url": "http://dataset1", "spotid": "source1"},  # Missing Header
            {"url": "https://dataset2", "spotid": "source2", "header": "source2"},  # bad Type
            {"url": "dataset2", "spotid": "source2", "header": ["source2", "srouce3"]}  # url error
        ]

        # Envoyer la requête POST
        with app.test_client() as client:
            response = client.post('/', json=invalid_data)

            # Vérifier que la réponse a un statut 400
            self.assertEqual(response.status_code, 400)
            # Vérifier que la réponse contient les erreurs de validation
            self.assertIn('error', response.json)
            self.assertEqual({'header': ['Missing data for required field.']}, response.json['error']['0'])
            self.assertEqual({'header': ['Not a valid list.']}, response.json['error']['1'])
            self.assertEqual({'url': ['Invalid value.']}, response.json['error']['2'])
