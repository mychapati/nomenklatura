from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from nomenklatura.core import db
from nomenklatura.schema import types
from nomenklatura.model import Statement, Context


def expand(entity_id):
    entity_ids = set([entity_id])
    while True:
        stmt = aliased(Statement)
        ctx = aliased(Context)
        q = db.session.query(stmt.subject, stmt._value)
        q = q.filter(stmt.deleted_at == None) # noqa
        q = q.filter(stmt.attribute == types.Object.attributes.same_as.name) # noqa
        q = q.filter(stmt.context_id == ctx.id)
        q = q.filter(ctx.active == True) # noqa
        q = q.filter(or_(
            and_(stmt.subject.in_(entity_ids), ~stmt._value.in_(entity_ids)),
            and_(~stmt.subject.in_(entity_ids), stmt._value.in_(entity_ids))
        ))
        has_fresh = False
        for (subject, value) in q.all():
            has_fresh = True
            entity_ids.update((subject, value))
        if not has_fresh:
            break
    return entity_ids


def match(left_id, right_id):
    return right_id in expand(left_id)
