import random as rand
import stomp
from app.utils.logger import logger


class StompListener(stomp.ConnectionListener):
    def __init__(self, connection):
        self.connection = connection

    def on_error(self, frame):
        logger.error('received an error "%s"' % frame.body)

    def on_message(self, frame):
        logger.debug('received a message : "%s"' % frame.body)
        for subscriber in self.connection.list_subscribers:
            if subscriber.str_id() == str(frame.headers['subscription']):
                subscriber.listener(frame.body)
                break
        pass

    def on_disconnected(self):
        logger.info('Stomp client disconnected, try to reconnect')
        self.connection.connected()


class StompController:
    list_subscribers = []

    def __init__(self):
        self.stomp_client = None
        self.connection = stomp.Connection([("localhost", 61613)])
        self.connection.set_listener('', StompListener(self))
        logger.debug('StompController initialized, connection set up')

    def connected(self):
        logger.debug('Connecting to STOMP server...')
        try:
            self.connection.connect('myuser', 'mypwd', wait=True)
            logger.info('Stomp client connected successfully')
            for subscriber in self.list_subscribers:
                self.connection.subscribe(destination=subscriber.destination, id=subscriber.str_id(), ack='auto')
                logger.debug(f'Subscribed to {subscriber.destination}')
        except Exception as e:
            logger.error(f"Failed to connect to STOMP server: {e}")

    def add_subscriber(self, queues_name, listener):
        logger.debug(f'Adding subscriber for queue {queues_name}')
        try:
            subscriber = Subscriber(queues_name, listener)
            self.list_subscribers.append(subscriber)
            self.connection.subscribe(destination=subscriber.destination, id=subscriber.str_id(), ack='auto')
            logger.debug(f'Subscriber added to {queues_name}')
        except Exception as e:
            logger.error(f"Error adding subscriber: {e}")

    def remove_subscriber(self, queues_name):
        logger.debug(f'Removing subscriber from {queues_name}')
        try:
            for subscriber in self.list_subscribers:
                if subscriber.destination == queues_name:
                    self.list_subscribers.remove(subscriber)
                    self.connection.unsubscribe(id=subscriber.str_id())
                    logger.debug(f'Subscriber removed from {queues_name}')
                    break
        except Exception as e:
            logger.error(f"Error removing subscriber: {e}")

    def send_message(self, destination, body):
        logger.debug(f'Sending message to {destination} with body: {body}')
        try:
            self.connection.send(body=body, destination=destination)
            logger.info(f'Message successfully sent to {destination}')
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message à {destination}: {e}")
            raise

    def __del__(self):
        logger.debug('Disconnecting from STOMP server')
        try:
            self.connection.disconnect()
            logger.info('Stomp client disconnected successfully')
        except Exception as e:
            logger.error(f"Error disconnecting from STOMP server: {e}")


class Subscriber:
    def __init__(self, destination, listener):
        self.id = rand.randint(1, 1000000)
        self.destination = destination
        self.listener = listener

    def str_id(self):
        return str(self.id)

    def __str__(self):
        return f'queue : {self.destination}'
