import logging

from loom.model import db
from loom.services.opencorp import OpenCorporatesService
from loom.services.offshoreleaks import OffshoreLeaksService
from loom.services.panama import PanamaService
from loom.services.secedgar import SECEDGARService

log = logging.getLogger(__name__)

SERVICES = {
    'opencorp': OpenCorporatesService,
    'secedgar': SECEDGARService,
    'panama': PanamaService,
    'offshoreleaks': OffshoreLeaksService
}


def lookup(service, node, label):
    try:
        svc = SERVICES.get(service)(node.graph)
        svc.lookup(node, label)
        db.session.commit()
    except Exception, e:
        log.exception(e)
