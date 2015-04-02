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
    db.create_all()


@manager.command
def dedupe():
    from nomenklatura.processing.deduper import dedupe_generate_pairings
    dedupe_generate_pairings()


@manager.command
def enrich(spider, entity_id):
    from nomenklatura.enrichment import get_spiders
    from nomenklatura.query import EntityQuery
    entity = EntityQuery.by_id(entity_id)
    assert entity is not None, "Entity was not found"
    cls = get_spiders().get(spider)
    assert cls is not None, "Spider was not found"
    print 'Spider:', cls
    cls().lookup(entity)


def main():
    manager.run()


if __name__ == '__main__':
    main()
