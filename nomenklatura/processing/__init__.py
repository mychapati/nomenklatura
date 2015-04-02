from flask.ext.sqlalchemy import models_committed

from nomenklatura.core import celery as app
from nomenklatura.model import Statement
from nomenklatura.processing.deduper import generate_pairings # noqa
from nomenklatura.processing.deduper import request_pairing # noqa
from nomenklatura.processing import reason_same_as


@models_committed.connect
def session_commit(signal, changes=None):
    for obj, op in changes:
        if not isinstance(obj, Statement):
            continue
        data = obj.to_dict(raw=True)
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        process_statement.delay(data, op)


@app.task
def process_statement(data, op):
    reason_same_as.handle(data, op)
