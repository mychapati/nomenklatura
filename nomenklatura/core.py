import logging

from archivekit import open_archive
from normality import slugify
from flask import Flask
from flask import url_for as _url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask.ext.login import LoginManager
from flask.ext.assets import Environment
from flask.ext.migrate import Migrate
from kombu import Exchange, Queue
from celery import Celery

from nomenklatura import default_settings

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('passlib').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('amqp').setLevel(logging.WARNING)

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('NOMENKLATURA_SETTINGS', silent=True)

app_title = app.config.get('APP_TITLE', 'Nomenklatura')
app_name = app.config.get('APP_NAME', slugify(app_title, sep='_'))

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=app.config.get('ALEMBIC_DIR'))

assets = Environment(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

celery = Celery(app_name, broker=app.config['CELERY_BROKER_URL'])

queue_name = app_name + '_q'
app.config['CELERY_DEFAULT_QUEUE'] = queue_name
app.config['CELERY_QUEUES'] = (
    Queue(queue_name, Exchange(queue_name), routing_key=queue_name),
)

celery = Celery(app_name, broker=app.config['CELERY_BROKER_URL'])
celery.config_from_object(app.config)

archive = open_archive(app.config.get('ARCHIVE_TYPE'),
                       **app.config.get('ARCHIVE_CONFIG'))


def url_for(*a, **kw):
    try:
        kw['_external'] = True
        return _url_for(*a, **kw)
    except RuntimeError:
        return None
