import json
import unittest
from unittest.mock import MagicMock, patch

from app.controllers.stomp_controller import StompListener, StompController, StompMultipleSend, \
    AdvancedStompTransaction, Subscriber


# Importer les classes à tester


class TestStompListener(unittest.TestCase):
    def test_on_message_success(self):
        connection_mock = MagicMock()
        listener = StompListener(connection_mock)
        frame = MagicMock()
        frame.body = json.dumps({"key": "value"})
        frame.headers = {'subscription': 'sub1', 'message-id': 'msg1'}

        # Simuler un abonné
        connection_mock.subscribers = [{'destination': 'sub1', 'listener': MagicMock()}]

        listener.on_message(frame)

        # Vérifier que le listener a été appelé
        connection_mock.subscribers[0]['listener'].assert_called_once_with(frame.body)
        connection_mock.connection.ack.assert_called_once_with('msg1', 'sub1')

    def test_on_message_failure(self):
        connection_mock = MagicMock()
        listener = StompListener(connection_mock)
        frame = MagicMock()
        frame.body = json.dumps({"key": "value"})
        frame.headers = {'subscription': 'sub1', 'message-id': 'msg1'}

        # Simuler un abonné qui lève une exception
        connection_mock.subscribers = [{'destination': 'sub1', 'listener': MagicMock(side_effect=Exception("Error"))}]

        listener.on_message(frame)

        # Vérifier que le message a été NACK
        connection_mock.connection.nack.assert_called_once_with('msg1', 'sub1')

    def test_on_disconnected(self):
        connection_mock = MagicMock()
        listener = StompListener(connection_mock)

        listener.on_disconnected()

        # Vérifier que la méthode de reconnexion a été appelée
        connection_mock._connect_with_retry.assert_called_once()


class TestStompController(unittest.TestCase):
    @patch('app.controllers.stomp_controller.stomp.Connection')
    def test_init_connection_success(self, mock_connection):
        mock_connection.return_value = MagicMock()

        controller = StompController()
        controller._init_connection()
        self.assertTrue(controller.is_connected)

    @patch('app.controllers.stomp_controller.stomp.Connection')
    def test_init_connection_failure(self, mock_connection):
        mock_connection.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            StompController()._init_connection()

    def test_add_subscriber(self):
        controller = StompController()
        controller.is_connected = True
        controller.connection = MagicMock()
        controller.add_subscriber('destination1')

        self.assertEqual(len(controller.subscribers), 1)
        self.assertEqual(controller.subscribers[0]['destination'], 'destination1')

    def test_send_message(self):
        controller = StompController()
        controller.connection = MagicMock()
        controller.send_message('destination1', {'key': 'value'})

        controller.connection.send.assert_called_once()
        self.assertIn('persistent', controller.connection.send.call_args[1]['headers'])

    def test_disconnect(self):
        controller = StompController()
        controller.is_connected = True
        controller.connection = MagicMock()
        controller.disconnect()

        controller.connection.disconnect.assert_called_once()
        self.assertFalse(controller.is_connected)


class TestStompMultipleSend(unittest.TestCase):
    def test_send(self):
        stomp_client_mock = MagicMock()
        multiple_send = StompMultipleSend(stomp_client_mock, 'destination1')

        multiple_send.send('message body')

        stomp_client_mock.send.assert_called_once_with(destination='destination1', body='message body',
                                                       transaction=multiple_send.txid)

    def test_send_error(self):
        stomp_client_mock = MagicMock()
        stomp_client_mock.send.side_effect = Exception("Send error")
        multiple_send = StompMultipleSend(stomp_client_mock, 'destination1')

        with self.assertRaises(Exception):
            multiple_send.send('message body')

        stomp_client_mock.abort.assert_called_once_with(multiple_send.txid)


class TestAdvancedStompTransaction(unittest.TestCase):
    def test_send_success(self):
        stomp_client_mock = MagicMock()
        stomp_client_mock.connection = MagicMock()
        transaction = AdvancedStompTransaction(stomp_client_mock, 'destination1')

        transaction.send({'key': 'value'})

        self.assertEqual(transaction.message_count, 1)

    def test_send_exceed_memory_limit(self):
        stomp_client_mock = MagicMock()
        stomp_client_mock.connection = MagicMock()
        transaction = AdvancedStompTransaction(stomp_client_mock, 'destination1', max_message_size=10)

        with self.assertRaises(ValueError):
            transaction.send('a' * 20)  # Exceeding the limit

    def test_commit(self):
        stomp_client_mock = MagicMock()
        stomp_client_mock.connection = MagicMock()
        transaction = AdvancedStompTransaction(stomp_client_mock, 'destination1')

        transaction.send({'key': 'value'})
        transaction.commit()

        stomp_client_mock.connection.commit.assert_called_once_with(transaction.txid)

    def test_handle_error(self):
        stomp_client_mock = MagicMock()
        stomp_client_mock.connection = MagicMock()
        transaction = AdvancedStompTransaction(stomp_client_mock, 'destination1')

        transaction._handle_error()

        stomp_client_mock.connection.abort.assert_called_once_with(transaction.txid)


class TestSubscriber(unittest.TestCase):
    def test_str_id(self):
        subscriber = Subscriber('destination1', MagicMock())
        self.assertIsInstance(subscriber.str_id(), str)

    def test_str(self):
        subscriber = Subscriber('destination1', MagicMock())
        self.assertEqual(str(subscriber), 'queue : destination1')


if __name__ == '__main__':
    unittest.main()
