from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from flask.ext.migrate import MigrateCommand, upgrade

from nomenklatura.core import db
from nomenklatura.views import app
from nomenklatura.assets import assets

manager = Manager(app)
manager.add_command('assets', ManageAssets(assets))
manager.add_command('db', MigrateCommand)


@manager.command
def sync():
    """ Sync or create the database. """
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS hstore;")
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")
    upgrade()
    # db.create_all()


@manager.command
def enrich(entity_id, spider=None):
    from nomenklatura.enrichment import enrich_entity
    enrich_entity(entity_id, spider=spider)


def main():
    manager.run()


if __name__ == '__main__':
    main()
