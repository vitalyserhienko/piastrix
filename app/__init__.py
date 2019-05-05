import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from wtforms.csrf.session import CSRF

app = Flask(__name__)

# app configuration
app.config.from_object('app.config')

# blueprints registration
from web import views
app.register_blueprint(views.pages)

# logging config
handler = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=1)
formatter = \
    logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
