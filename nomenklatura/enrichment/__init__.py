import logging
from pkg_resources import iter_entry_points

from nomenklatura.core import db, celery
from nomenklatura.query import EntityQuery

log = logging.getLogger(__name__)


def get_spiders():
    spiders = {}
    for ep in iter_entry_points('nomenklatura.spiders'):
        spiders[ep.name] = ep.load()
    return spiders


@celery.task
def enrich_entity(entity_id, spider=None):
    entity = EntityQuery.by_id(entity_id)
    if entity is None:
        log.error('Entity does not exist: %s', entity_id)
        return

    for name, cls in get_spiders().items():
        if spider is not None and spider != name:
            continue

        try:
            inst = cls()
            inst.lookup(entity)
            db.session.commit()
        except Exception, e:
            log.exception(e)
            db.session.rollback()
