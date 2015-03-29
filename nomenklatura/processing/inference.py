import logging
from sqlalchemy import exists, and_
from sqlalchemy.orm import aliased

from nomenklatura.core import db, celery
from nomenklatura.schema import attributes
from nomenklatura.model.statement import Statement

log = logging.getLogger(__name__)


def delete_inferred_statements():
    q = db.session.query(Statement)
    q = q.filter(Statement.inferred == True) # noqa
    q.delete()


def generate_same_as_copies():
    # TODO: this should be recursive, but that seems a bit too weird?
    stmt = aliased(Statement)
    sa_stmt = aliased(Statement)
    ex_stmt = aliased(Statement)
    q = db.session.query(sa_stmt.subject, stmt._attribute, stmt._value,
                         stmt.context_id)
    q = q.filter(and_(
        stmt._attribute != attributes.same_as.name,
        sa_stmt._attribute == attributes.same_as.name,
        sa_stmt._value == stmt.subject
    ))

    q = q.filter(~exists().where(and_(
        ex_stmt.subject == sa_stmt.subject,
        ex_stmt._attribute == stmt._attribute,
        ex_stmt._value == stmt._value,
        ex_stmt.context_id == sa_stmt.context_id,
    )))

    i = -1
    for i, row in enumerate(q):
        s, a, v, c = row
        inf = Statement(s, attributes[a], None, None)
        inf.inferred = True
        inf._value = v
        inf.context_id = c
        db.session.add(inf)

    log.info("Generated %s 'same_as' statement copies.", i + 1)
    db.session.flush()


@celery.task
def generate_inferred():
    delete_inferred_statements()
    db.session.flush()
    generate_same_as_copies()
    db.session.commit()
