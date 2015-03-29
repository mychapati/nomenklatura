from os import path

DEBUG = True
SECRET_KEY = 'no'
APP_NAME = 'nomenklatura'
SQLALCHEMY_DATABASE_URI = 'sqlite:///master.sqlite3'
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
DEFAULT_ROLE = 'read'

ARCHIVE_TYPE = 'file'
ARCHIVE_CONFIG = {'path': '/Users/fl/Data/nk-uploads'}

ALLOWED_EXTENSIONS = set(['csv', 'tsv', 'ods', 'xls', 'xlsx', 'txt'])

ALEMBIC_DIR = path.join(path.dirname(__file__), 'migrate')
ALEMBIC_DIR = path.abspath(ALEMBIC_DIR)

CELERY_ALWAYS_EAGER = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_IMPORTS = (
    'nomenklatura.processing',
    'nomenklatura.processing.imports',
    'nomenklatura.processing.inference',
    'nomenklatura.processing.deduper',
)

MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_DEBUG = True
MAIL_DEFAULT_SENDER = 'nomenklatura@grano.cc'
