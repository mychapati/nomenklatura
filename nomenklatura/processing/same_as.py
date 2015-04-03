from datetime import datetime
import logging

from nomenklatura.core import db
from nomenklatura.schema import types
from nomenklatura.schema.util import date_parse
from nomenklatura.model import Statement

log = logging.getLogger(__name__)
SKIP_ATTRIBUTES = [types.Object.attributes.same_as,
                   types.Object.attributes.type]


def sync_statement(stmt, same_as, op):
    if stmt['attribute'] in SKIP_ATTRIBUTES:
        return

    via = '%s>>%s' % (same_as['id'], stmt['id'])
    q = db.session.query(Statement)
    q = q.filter(Statement.context_id == same_as['context_id'])
    q = q.filter(Statement.inferred_via == via)
    stmt_inf = q.first()

    if stmt_inf is None:
        stmt_inf = Statement(same_as['value'], stmt['attribute'],
                             None, None)
        stmt_inf.context_id = same_as['context_id']
        stmt_inf.inferred_via = via

    if op == 'delete' or stmt['deleted_at'] or same_as['deleted_at']:
        stmt_inf.deleted_at = date_parse(stmt['deleted_at']) or \
            date_parse(same_as['deleted_at']) or datetime.utcnow()
    else:
        stmt_inf.deleted_at = None

    stmt_inf.value = stmt['value']
    log.info('Inferred statement %s -> %s -> %s via same_as %s',
             same_as['value'], stmt['attribute'], stmt['value'], via)
    db.session.add(stmt_inf)


def handle(data, op):
    same_as_attr = types.Object.attributes.same_as.name
    if data['attribute'] == same_as_attr:
        q = db.session.query(Statement)
        q = q.filter(Statement.subject == data['subject'])
        q = q.filter(Statement.attribute != same_as_attr)
        for stmt in q:
            if stmt.active:
                sync_statement(stmt.to_dict(raw=True), data, op)
    else:
        q = db.session.query(Statement)
        q = q.filter(Statement.subject == data['subject'])
        q = q.filter(Statement.attribute == same_as_attr)
        for stmt in q:
            if stmt.active:
                sync_statement(data, stmt.to_dict(raw=True), op)

    db.session.commit()
