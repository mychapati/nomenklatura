from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import MigrateCommand, upgrade

from nomenklatura.core import db
from nomenklatura.views import app
from nomenklatura.assets import assets
from nomenklatura.fixtures import import_fixtures
from nomenklatura.processing.imports import import_file_sync


manager = Manager(app)
manager.add_command('assets', ManageAssets(assets))
manager.add_command('db', MigrateCommand)


@manager.command
def sync():
    """ Sync or create the database. """
    upgrade()
    # db.create_all()


@manager.command
def enrich(entity_id, spider=None):
    from nomenklatura.enrichment import enrich_entity
    enrich_entity(entity_id, entity_id, spider=spider)


@manager.command
def load(model_file, data_file):
    """ Import a data file with properties specified in the model file. """
    import_file_sync(model_file, data_file)


@manager.command
def fixtures():
    """ Import fixture objects, such as countries. """
    import_fixtures()


def main():
    manager.run()


if __name__ == '__main__':
    main()
