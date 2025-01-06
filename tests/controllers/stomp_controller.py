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
import unittest
from unittest.mock import MagicMock, patch

from app.controllers.stomp_controller import StompController, StompListener  # Replace with actual import paths


class TestStompController(unittest.TestCase):

    @patch('app.controllers.stomp_controller.logger')  # Mock the logger to prevent actual logging during tests
    @patch('stomp.Connection')  # Mock the stomp.Connection class
    def setUp(self, mock_stomp_connection, mock_logger):
        self.mock_connection = MagicMock()
        self.logger = MagicMock()
        mock_logger.return_value = self.logger
        mock_stomp_connection.return_value = self.mock_connection  # Return mocked connection when stomp.Connection() is called
        self.controller = StompController()  # Instance of the controller

    def test_connected(self):
        """Test that the controller connects to the stomp server and subscribes."""
        # Simulate the connected method
        self.mock_connection.connect.assert_called()

        self.controller.connected()

        self.mock_connection.connect.assert_called_with('myuser', 'mypwd', wait=True)

        # Check if the connect method was called with correct parameters

        # Check if the logger info method was called
        # self.logger.info.assert_called_with('Stomp client connected')

    def test_add_subscriber(self):
        """Test that a subscriber is added correctly."""
        mock_listener = MagicMock()  # Mock the listener

        # Call add_subscriber to add a subscriber
        self.controller.add_subscriber('queue1', mock_listener)

        # Check if the subscriber was added to the list
        self.assertEqual(len(self.controller.list_subscribers), 1)

        # Check if the connection subscribe method was called
        self.mock_connection.subscribe.assert_called_once_with(
            destination='queue1', id=self.controller.list_subscribers[0].str_id(), ack='auto'
        )

    def test_send_message(self):
        """Test that a message is sent correctly."""
        # Call send_message to send a message
        self.controller.send_message('queue1', 'Test message')

        # Check if the send method was called with the correct parameters
        self.mock_connection.send.assert_called_once_with(
            body='Test message', destination='queue1'
        )

    def test_on_disconnected(self):
        """Test that the on_disconnected method tries to reconnect."""
        listener = StompListener(self.controller)

        # Simulate the on_disconnected callback
        listener.on_disconnected()

        # Check if the connected method was called after disconnect
        self.mock_connection.connect.assert_called()


if __name__ == '__main__':
    unittest.main()
