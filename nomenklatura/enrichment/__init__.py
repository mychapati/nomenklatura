import logging
from pkg_resources import iter_entry_points

from nomenklatura.core import db

log = logging.getLogger(__name__)


def get_spiders():
    spiders = {}
    for ep in iter_entry_points('nomenklatura.spiders'):
        spiders[ep.name] = ep.load()
    return spiders


def lookup(service, node, label):
    try:
        svc = spiders.get(service)(node.graph)
        svc.lookup(node, label)
        db.session.commit()
    except Exception, e:
        log.exception(e)
