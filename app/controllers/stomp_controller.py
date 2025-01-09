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

import os
import random as rand

import stomp

from app.utils.logger import logger


class StompListener(stomp.ConnectionListener):
    def __init__(self, connection):
        self.connection = connection

    def on_error(self, frame):
        logger.error('received an error "%s"' % frame.body)

    def on_message(self, frame):
        body = frame.body
        logger.debug('received a message : "%s"' % body)

        for subscriber in self.connection.list_subscribers:
            if subscriber.str_id() == str(frame.headers['subscription']):
                try:
                    subscriber.listener(body)
                except Exception as e:
                    self.connection.connection.nack(frame.headers['message-id'], subscriber.str_id())
                    break
                self.connection.connection.ack(frame.headers['message-id'], subscriber.str_id())
                break
        pass

    def on_disconnected(self):
        logger.info('Stomp client disconnected, try to reconnect')
        self.connection.connected()


class StompController:
    list_subscribers = []


    def __init__(self):
        self.stomp_client = None
        self.connection = stomp.Connection([(os.environ.get('QUEHOST') or "", int(os.environ.get('QUEPORT') or 61613))])
        self.connection.set_listener('', StompListener(self))
        # self.connected()

    def connected(self):
        self.connection.connect(os.environ['QUEUSER'], os.environ['QUEPASS'], wait=True)
        logger.info('Stomp client connected')
        self.subscriber()

    def add_subscriber(self, queues_name, listener):
        logger.debug('Add subscribe to queue : %s' % queues_name)
        subscriber = Subscriber(queues_name, listener)
        self.list_subscribers.append(subscriber)
        self.connection.subscribe(destination=subscriber.destination, id=subscriber.str_id(), ack='client')

    def remove_subscriber(self, queues_name):
        for subscriber in self.list_subscribers:
            if subscriber.destination == queues_name:
                self.list_subscribers.remove(subscriber)
                self.connection.unsubscribe(id=subscriber.str_id())
                break

    def un_subscriber(self):
        for subscriber in self.list_subscribers:
            self.connection.unsubscribe(id=subscriber.str_id())

    def subscriber(self):
        for subscriber in self.list_subscribers:
            self.connection.subscribe(destination=subscriber.destination, id=subscriber.str_id(), ack='client')

    def send_message(self, destination, body):
        logger.debug('send a message : "%s"' % body)
        self.connection.send(body=body, destination=destination)

    def __del__(self):
        self.connection.disconnect()


class StompMultipleSend:
    def __init__(self, stomp_client, destination):
        self.stomp_client = stomp_client
        self.txid = self.stomp_client.begin()
        self.destination = destination

    def send(self, body):
        self.stomp_client.send(destination=self.destination, body=body, transaction=self.txid)

    def __del__(self):
        logger.info("Stomp : Send all message")
        self.stomp_client.commit(self.txid)


class Subscriber:
    def __init__(self, destination, listener):
        self.id = rand.randint(1, 1000000)
        self.destination = destination
        self.listener = listener

    def str_id(self):
        return str(self.id)

    def __str__(self):
        return f'queue : {self.destination}'
