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
from unittest import TestCase

from flask import Flask

from app.controllers.data_controller import data_controller

# Créer une application Flask pour tester
app = Flask(__name__)
app.register_blueprint(data_controller)


# Fonction globale utilisée dans le processus
def mock_process(data_service_function, valid_data):
    """
    Simule l'importation des données en appelant une fonction simulée.
    """
    data_service_function(valid_data)


class TestDataController(TestCase):

    def setUp(self):
        # Préparer l'environnement pour les tests
        self.client = app.test_client()

    #
    #    @patch('app.services.data_service.DataService.import_data')  # Mock le service d'importation des données
    #    def test_make_dataset_success(self, mock_import_data):
    #        # Exemple de données valides
    #        valid_data = [
    #            {"url": "https://prout.fr/", "spotid": "csv", "header": ["source1", "srouce3"]},
    #            {"url": "http://prout.fr/", "spotid": "json", "header": ["source2", "srouce3"]}
    #        ]
    #
    #
    #        # Créer un processus "daemon" pour ne pas bloquer les tests
    #        process = Process(target=mock_process, args=(mock_import_data, valid_data), daemon=True)
    #        process.start()
    #        process.join()
    #
    #        # Vérifier que l'importation de données a bien été simulée dans le mock
    #        mock_import_data.assert_called_once_with(valid_data)
    #
    #        # Envoyer la requête POST avec Flask test client
    #        with app.test_client() as client:
    #            response = client.post('/', json=valid_data)
    #
    #            # Vérifier que la réponse a un statut 200
    #            self.assertEqual(response.status_code, 200)
    #            self.assertEqual(response.json, "ok")
    #
    #            # Vérifier à nouveau que le service d'importation de données a été appelé
    #            mock_import_data.assert_called_once()
    #
    def test_make_dataset_invalid_data(self):
        # Exemple de données invalides (manque de champ "type")
        invalid_data = [
            {"url": "http://dataset1", "spotid": "source1"},  # Missing Header
            {"url": "https://dataset2", "spotid": "source2", "header": "source2"},  # bad Type
            {"url": "dataset2", "spotid": "source2", "header": ["source2", "srouce3"]}  # url error
        ]

        # Tester en envoyant la requête POST avec l'application Flask
        with app.test_client() as client:
            response = client.post('/', json=invalid_data)

            # Vérifier que la réponse a un statut 400
            self.assertEqual(response.status_code, 400)

            # Vérifier que la réponse contient les erreurs de validation
            self.assertIn('error', response.json)
            self.assertEqual({'header': ['Missing data for required field.']}, response.json['error']['0'])
            self.assertEqual({'header': ['Not a valid list.']}, response.json['error']['1'])
            self.assertEqual({'url': ['Invalid value.']}, response.json['error']['2'])
