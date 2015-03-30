import logging

from nomenklatura.core import db
from nomenklatura.enrichment.opencorp import OpenCorporatesService
from nomenklatura.enrichment.offshoreleaks import OffshoreLeaksService
from nomenklatura.enrichment.panama import PanamaService
from nomenklatura.enrichment.secedgar import SECEDGARService

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
