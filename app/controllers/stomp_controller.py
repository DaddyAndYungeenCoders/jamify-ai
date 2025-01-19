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
import json
import os
import queue
import random as rand
import threading
import time
from typing import Any, List, Optional, Dict, Callable, Union

import stomp

from app.utils.logger import logger


class StompListener(stomp.ConnectionListener):
    def __init__(self, connection):
        self.connection = connection

    def on_error(self, frame):
        logger.error('received an error "%s"' % frame.body)

    def on_message(self, frame):
        body = frame.body
        # logger.debug('received a message : "%s"' % body)

        for subscriber in self.connection.subscribers:
            if subscriber['destination'] == str(frame.headers['subscription']):
                try:
                    subscriber['listener'](body)
                except Exception as e:
                    self.connection.connection.nack(frame.headers['message-id'], subscriber['destination'] )
                    break
                self.connection.connection.ack(frame.headers['message-id'], subscriber['destination'] )
                break
        pass

    def on_disconnected(self):
        logger.info('Stomp client disconnected, try to reconnect')
        self.connection._connect_with_retry()


class StompController:
    DEFAULT_CONFIG = {
        'HOST': os.environ.get('QUEHOST', 'localhost'),
        'PORT': int(os.environ.get('QUEPORT', 61613)),
        'USER': os.environ.get('QUEUSER', 'admin'),
        'PASS': os.environ.get('QUEPASS', 'password'),
        'RECONNECT_ATTEMPTS': 5,
        'RECONNECT_DELAY': 5,
        'MAX_QUEUE_SIZE': 1000,
        'MESSAGE_TTL': 3600,  # 1 heure
        'HEARTBEAT_INTERVAL': 30000,  # 30 secondes
    }

    def __init__(
            self,
            config: Optional[Dict[str, Any]] = None,
            custom_listener: Optional[Callable] = None
    ):
        """
        Initialise un contrôleur STOMP avancé

        :param config: Configuration personnalisée
        :param custom_listener: Listener personnalisé
        """
        # Fusionner la configuration par défaut avec la configuration personnalisée
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        # Gestion des files d'attente
        self.message_queue = queue.Queue(maxsize=self.config['MAX_QUEUE_SIZE'])
        self.processing_thread = None

        # Gestion des abonnements
        self.subscribers: List[Dict[str, Any]] = []

        # État de connexion
        self.connection = None
        self.is_connected = False
        self.connection_lock = threading.Lock()

        # Listener personnalisé ou par défaut
        self.listener = custom_listener or self._default_message_handler

        # Initialisation de la connexion
        self._init_connection()

    def _init_connection(self):
        """
        Initialisation de la connexion STOMP
        """
        try:
            # Configuration de la connexion
            self.connection = stomp.Connection(
                [(self.config['HOST'], self.config['PORT'])],
                heartbeats=(
                    self.config['HEARTBEAT_INTERVAL'],
                    self.config['HEARTBEAT_INTERVAL']
                )
            )

            # Définition du listener
            self.connection.set_listener(
                'advanced_listener',
                StompListener(self)
            )

            # Tentative de connexion
            self._connect_with_retry()

            # Démarrage du thread de traitement des messages
            self._start_message_processing()

        except Exception as e:
            logger.error(f"Erreur d'initialisation de la connexion : {e}")
            raise

    def create_transaction(
            self,
            destination: str,
            max_messages: Optional[int] = None,
            max_memory_limit: Optional[int] = None,
            max_message_size: Optional[int] = None
    ) -> 'AdvancedStompTransaction':
        """
        Crée une nouvelle transaction STOMP

        :param destination: Destination des messages
        :param max_messages: Nombre maximum de messages par transaction
        :param max_memory_limit: Limite mémoire totale
        :param max_message_size: Taille maximale d'un message
        :return: Instance de AdvancedStompTransaction
        """
        return AdvancedStompTransaction(
            stomp_client=self,
            destination=destination,
            max_messages=max_messages or 10000,
            max_memory_limit=max_memory_limit or (512 * 1024 * 1024),  # 512 Mo
            max_message_size=max_message_size or (10 * 1024 * 1024)  # 10 Mo
        )

    def _connect_with_retry(self):
        """
        Tentative de connexion avec mécanisme de retry
        """
        for attempt in range(self.config['RECONNECT_ATTEMPTS']):
            try:
                with self.connection_lock:
                    self.connection.connect(
                        self.config['USER'],
                        self.config['PASS'],
                        wait=True
                    )
                    self.is_connected = True

                logger.info("Connexion STOMP établie avec succès")

                # Réabonnement aux files existantes
                self._resubscribe_all()
                return

            except Exception as e:
                logger.warning(f"Tentative de connexion {attempt + 1} échouée : {e}")
                time.sleep(self.config['RECONNECT_DELAY'])

        raise ConnectionError("Impossible d'établir une connexion STOMP")

    def _start_message_processing(self):
        """
        Démarrage du thread de traitement des messages
        """
        self.processing_thread = threading.Thread(
            target=self._process_message_queue,
            daemon=True
        )
        self.processing_thread.start()

    def _process_message_queue(self):
        """
        Traitement asynchrone des messages en file d'attente
        """
        while True:
            try:
                # Récupération du message avec timeout
                message = self.message_queue.get(timeout=1)

                try:
                    # Traitement du message
                    self.listener(message)
                except Exception as e:
                    logger.error(f"Erreur de traitement du message : {e}")

                # Marquer le message comme traité
                self.message_queue.task_done()

            except queue.Empty:
                # Attente si la file est vide
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Erreur dans le traitement de la file : {e}")

    def _default_message_handler(self, message: Dict[str, Any]):
        """
        Gestionnaire de message par défaut

        :param message: Message reçu
        """
        logger.info(f"Message reçu : {message}")

    def add_subscriber(
            self,
            destination: str,
            listener: Optional[Callable] = None,
            ack_mode: str = 'client'
    ):
        """
        Ajout d'un abonnement

        :param destination: Destination de la file
        :param listener: Gestionnaire de message personnalisé
        :param ack_mode: Mode d'accusé de réception
        """
        subscriber = {
            'destination': destination,
            'listener': listener or self.listener,
            'ack_mode': ack_mode
        }

        self.subscribers.append(subscriber)

        if self.is_connected:
            self._subscribe(subscriber)

    def _subscribe(self, subscriber: Dict[str, Any]):
        """
        Abonnement à une file

        :param subscriber: Informations de l'abonnement
        """
        try:
            self.connection.subscribe(
                destination=subscriber['destination'],
                id=subscriber['destination'],
                ack=subscriber['ack_mode']
            )
            logger.info(f"Abonnement à {subscriber['destination']} réussi")

        except Exception as e:
            logger.error(f"Erreur d'abonnement : {e}")

    def _resubscribe_all(self):
        """
        Réabonnement à toutes les files après reconnexion
        """
        for subscriber in self.subscribers:
            self._subscribe(subscriber)

    def send_message(
            self,
            destination: str,
            body: Union[str, Dict, List],
            persistent: bool = True,
            priority: int = 4,
            ttl: Optional[int] = None
    ):
        """
        Envoi d'un message

        :param destination: Destination du message
        :param body: Corps du message
        :param persistent: Message persistant
        :param priority: Priorité du message
        :param ttl: Durée de vie du message
        """
        try:
            # Préparation des headers
            headers = {
                'persistent': 'true' if persistent else 'false',
                'priority': str(priority)
            }

            # Ajout de la durée de vie si spécifiée
            if ttl:
                headers['expires'] = str(int((time.time() + ttl) * 1000))

            # Conversion du body
            if isinstance(body, (dict, list)):
                body = json.dumps(body)

            # Envoi du message
            self.connection.send(
                destination=destination,
                body=body,
                headers=headers
            )

            logger.debug(f"Message envoyé à {destination}")
        except Exception as e:
            logger.error(f"Erreur d'envoi de message : {e}")

    def disconnect(self):
        """
        Déconnexion du serveur STOMP
        """
        with self.connection_lock:
            if self.is_connected:
                self.connection.disconnect()
                self.is_connected = False
                logger.info("Déconnexion réussie")

    def __del__(self):
        """Nettoyage final"""
        self.disconnect()


class StompMultipleSend:
    def __init__(self, stomp_client, destination):
        self.stomp_client = stomp_client
        self.txid = self.stomp_client.begin()
        self.destination = destination

    def send(self, body):
        try:
            self.stomp_client.send(destination=self.destination, body=body, transaction=self.txid)
        except Exception as e:
            self.stomp_client.abort(self.txid)
            raise e

    def __del__(self):
        logger.info("Stomp : Send all message")
        self.stomp_client.commit(self.txid)


class AdvancedStompTransaction:
    # Configurations par défaut ActiveMQ
    DEFAULT_MAX_MEMORY_LIMIT = 512 * 1024 * 1024  # 512 Mo
    DEFAULT_MAX_MESSAGES = 10000
    DEFAULT_MESSAGE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 Mo par message

    def __init__(
            self,
            stomp_client: 'StompController',
            destination: str,
            max_messages: Optional[int] = None,
            max_memory_limit: Optional[int] = None,
            max_message_size: Optional[int] = None
    ):
        """
        Transaction avancée avec gestion intelligente des ressources

        :param stomp_client: Client STOMP
        :param destination: Destination des messages
        :param max_messages: Nombre max de messages par transaction
        :param max_memory_limit: Limite mémoire totale
        :param max_message_size: Taille maximale d'un message
        """
        self.stomp_client = stomp_client
        self.destination = destination

        # Configuration des limites
        self.max_messages = max_messages or self.DEFAULT_MAX_MESSAGES
        self.max_memory_limit = max_memory_limit or self.DEFAULT_MAX_MEMORY_LIMIT
        self.max_message_size = max_message_size or self.DEFAULT_MESSAGE_SIZE_LIMIT

        # Initialisation de la transaction
        self.txid = self.stomp_client.connection.begin()

        # Tracking des messages
        self.messages: List[Any] = []
        self.total_memory_used = 0

        # Métriques
        self.start_time = time.time()
        self.message_count = 0

        # Verrou pour la thread-safety
        self._lock = threading.Lock()

        # Unsubscibe to queue
        self.stomp_client.connection.unsubscribe(destination)


    def _validate_message(self, body: Any) -> bytes:
        """
        Validation et préparation du message

        :param body: Corps du message
        :return: Message sérialisé
        """
        # Conversion en JSON si nécessaire
        if isinstance(body, (dict, list)):
            body = json.dumps(body)

        # Conversion en bytes
        message_bytes = body.encode('utf-8') if isinstance(body, str) else body

        # Vérification de la taille
        if len(message_bytes) > self.max_message_size:
            logger.warning(f"Message trop volumineux. Taille: {len(message_bytes)} octets")
            raise ValueError(f"Message size exceeds limit of {self.max_message_size} bytes")

        return message_bytes

    def send(self, body: Any):
        """
        Envoi sécurisé de message

        :param body: Corps du message
        """
        with self._lock:
            try:
                # Validation du message
                message_bytes = self._validate_message(body)
                message_size = len(message_bytes)

                # Vérification des limites
                if (self.message_count >= self.max_messages or
                        self.total_memory_used + message_size > self.max_memory_limit):
                    # Auto-commit si les limites sont atteintes
                    self.commit()
                    # Nouvelle transaction
                    self.txid = self.stomp_client.connection.begin()
                    self.messages.clear()
                    self.total_memory_used = 0
                    self.message_count = 0

                # Envoi du message
                self.stomp_client.connection.send(
                    destination=self.destination,
                    body=message_bytes,
                    transaction=self.txid
                )

                # Mise à jour des métriques
                self.messages.append(body)
                self.total_memory_used += message_size
                self.message_count += 1

                # Log optionnel
                # logger.debug(f"Message envoyé. Taille: {message_size} octets")

            except Exception as e:
                logger.error(f"Erreur d'envoi de message: {e}")
                self._handle_error()

    def commit(self):
        """
        Commit de la transaction avec gestion des erreurs
        """
        try:
            # Commit si des messages existent
            if self.message_count > 0:
                self.stomp_client.connection.commit(self.txid)

                # Métriques de performance
                duration = time.time() - self.start_time
                logger.info(
                    f"Transaction commitée: "
                    f"Messages={self.message_count}, "
                    f"Mémoire={self.total_memory_used} octets, "
                    f"Durée={duration:.2f}s"
                )

            # Réinitialisation
            self._reset()

        except Exception as e:
            logger.error(f"Erreur de commit: {e}")
            self._handle_error()

    def _handle_error(self):
        """
        Gestion centralisée des erreurs
        """
        try:
            # Annulation de la transaction
            self.stomp_client.connection.abort(self.txid)
        except Exception as abort_error:
            logger.error(f"Erreur lors de l'annulation: {abort_error}")

        # Réinitialisation
        self._reset()

    def _reset(self):
        """
        Réinitialisation complète de la transaction
        """
        self.messages.clear()
        self.total_memory_used = 0
        self.message_count = 0
        self.start_time = time.time()

    def __enter__(self):
        """Support du context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit automatique à la sortie"""
        if exc_type is None:
            self.commit()
        else:
            self._handle_error()

    def __del__(self):
        """Nettoyage final"""
        try:
            self.commit()
            self.stomp_client._resubscribe_all()
        except Exception:
            self._handle_error()


class Subscriber:
    def __init__(self, destination, listener):
        self.id = rand.randint(1, 1000000)
        self.destination = destination
        self.listener = listener

    def str_id(self):
        return str(self.id)

    def __str__(self):
        return f'queue : {self.destination}'
