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

import logging

from flask import Flask

from app.controllers import main_blueprint


def create_app():
    app = Flask(__name__)

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_handler = logging.StreamHandler()
    werkzeug_handler.setFormatter(logging.Formatter('%(asctime)s-jamify-ai-flask-%(levelname)s-%(message)s'))
    werkzeug_logger.handlers = [werkzeug_handler]
    werkzeug_logger.setLevel(logging.ERROR)

    app.register_blueprint(main_blueprint)

    return app
