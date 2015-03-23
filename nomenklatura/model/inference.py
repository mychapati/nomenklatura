# TODO, write this in SQL
import logging
from itertools import count

from nomenklatura.core import db
from nomenklatura.model.statement import Statement
from nomenklatura.model.schema import attributes

log = logging.getLogger(__name__)


def clear():
    q = db.session.query(Statement)
    q = q.filter(Statement.inferred == True) # noqa
    q.delete()


def clone(src, subject):
    dst = Statement(src.dataset, subject, src.attribute, src.value,
                    src.context)
    dst.inferred = True
    dst.created_at = src.created_at
    db.session.add(dst)


def generate(mapping):
    count = 0
    q = db.session.query(Statement)
    q = q.filter(Statement.subject == mapping.subject)
    q = q.filter(Statement._attribute != attributes.same_as.name)
    for stmt in q:
        iq = db.session.query(Statement)
        iq = iq.filter(Statement.subject == mapping._value)
        iq = iq.filter(Statement._attribute == stmt._attribute)
        iq = iq.filter(Statement._value == stmt._value)
        iq = iq.filter(Statement.context_id == stmt.context_id)
        iq = iq.filter(Statement.inferred == True) # noqa
        if not iq.count():
            log.info("Cloning %r", stmt)
            clone(stmt, mapping._value)
            count += 1
    return count


def infer():
    clear()
    for i in count(1):
        log.info('Inference, iteration #%s', i)
        q = db.session.query(Statement)
        q = q.filter(Statement._attribute == attributes.same_as.name)
        if not sum([generate(s) for s in q]):
            break
    db.session.commit()
