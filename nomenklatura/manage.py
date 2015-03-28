from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import MigrateCommand, upgrade

from nomenklatura.core import db
from nomenklatura.views import app
from nomenklatura.assets import assets
from nomenklatura.model import inference, Dataset

manager = Manager(app)
manager.add_command('assets', ManageAssets(assets))
manager.add_command('db', MigrateCommand)


@manager.command
def sync():
    """ Sync or create the database. """
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS hstore;")
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")
    upgrade()
    db.create_all()


@manager.command
def infer(slug):
    """ Run inference of sameAs. """
    dataset = Dataset.by_slug(slug)
    inference.infer(dataset)


if __name__ == '__main__':
    manager.run()
