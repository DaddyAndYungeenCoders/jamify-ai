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
import unittest
from unittest.mock import MagicMock, patch

from app.controllers.stomp_controller import StompController, StompListener  # Replace with actual import paths


class TestStompController(unittest.TestCase):

    @patch('app.controllers.stomp_controller.logger')  # Mock the logger to prevent actual logging during tests
    @patch('app.controllers.stomp_controller.stomp.Connection')  # Mock the stomp.Connection class
    def setUp(self, mock_stomp_connection, mock_logger):
        # Mock the stomp.Connection instance
        self.mock_connection = MagicMock()

        # Ensure that the mock logger doesn't perform actual logging
        self.logger = MagicMock()
        mock_logger.return_value = self.logger

        # Retourner la connexion mockée lorsque stomp.Connection() est appelée
        mock_stomp_connection.return_value = self.mock_connection

        # Instancier le contrôleur
        self.controller = StompController()

    def test_connected(self):
        """Test that the controller connects to the stomp server and subscribes."""
        # Trigger the connected method
        self.controller.connected()

        # Check that the connect method was called on the mock connection
        self.mock_connection.connect.assert_called_once_with('myuser', 'mypwd', wait=True)

        # Optionally, check if the logger was called with the appropriate message
        # self.logger.info.assert_called_with('Stomp client connected')

    def test_add_subscriber(self):
        """Test that a subscriber is added correctly."""
        mock_listener = MagicMock()  # Mock the listener

        # Add a subscriber
        self.controller.add_subscriber('queue1', mock_listener)

        # Assert that the subscriber was added to the list
        self.assertEqual(len(self.controller.list_subscribers), 1)

        # Check that the subscribe method was called on the mock connection with correct parameters
        self.mock_connection.subscribe.assert_called_once_with(
            destination='queue1', id=self.controller.list_subscribers[0].str_id(), ack='auto'
        )

    def test_send_message(self):
        """Test that a message is sent correctly."""
        # Send a message
        self.controller.send_message('queue1', 'Test message')

        # Check that the send method was called on the mock connection with correct parameters
        self.mock_connection.send.assert_called_once_with(
            body='Test message', destination='queue1'
        )

    def test_on_disconnected(self):
        """Test that the on_disconnected method tries to reconnect."""
        listener = StompListener(self.controller)

        # Simulate the on_disconnected callback
        listener.on_disconnected()

        # Check if the connect method was called after disconnection
        self.mock_connection.connect.assert_called()


if __name__ == '__main__':
    unittest.main()
