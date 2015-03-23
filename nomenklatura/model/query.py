from sqlalchemy import exists, and_, or_
from sqlalchemy.orm import aliased, joinedload

from nomenklatura.core import db
from nomenklatura.model.schema import attributes
from nomenklatura.model.statement import Statement
from nomenklatura.model.context import Context
from nomenklatura.model.entity import Entity


class EntityQuery(object):

    def __init__(self, dataset=None, limit=None, offset=None, same_as=True):
        self._dataset = dataset
        self._limit = limit
        self._offset = offset
        self._same_as = same_as

    def clone(self, **kw):
        return EntityQuery(dataset=kw.get('dataset', self._dataset),
                           limit=kw.get('limit', self._limit),
                           offset=kw.get('offset', self._offset),
                           same_as=kw.get('same_as', self._same_as))

    def filter_dataset(self, dataset):
        return self.clone(dataset=dataset)

    def limit(self, n):
        return self.clone(limit=n)

    def offset(self, n):
        return self.clone(offset=n)

    def _stmt_q(self, main_stmt, q):
        stmt = aliased(Statement)
        ctx = aliased(Context)
        q = q.filter(main_stmt.subject == stmt.subject)
        q = q.filter(stmt.context_id == ctx.id)
        q = q.filter(ctx.active == True) # noqa
        return q, stmt

    def _sub_query(self, paginate=True):
        stmt = aliased(Statement)
        subj = stmt.subject.label('subject')
        q = db.session.query(subj)
        q = q.filter(stmt.dataset_id == self._dataset.id)

        # Filter out inferred identities (i.e. those which have 'same_as')
        if self._same_as:
            same_as = aliased(Statement)
            q = q.filter(~exists().where(and_(
                same_as._attribute == attributes.same_as.name,
                same_as.subject == stmt.subject
            )))

        q = q.distinct()
        if paginate:
            if self._limit is not None:
                q = q.limit(self._limit)
            if self._offset is not None:
                q = q.offset(self._offset)
        return q

    def _query(self, sq=None, id=None):
        stmt = aliased(Statement)
        q = db.session.query(stmt)
        q = q.options(joinedload(stmt.context))

        val = unicode(id)
        if sq is not None:
            ssq = sq.subquery()
            val = ssq.c.subject

        q = q.filter(stmt.subject == val)
        if not self._same_as:
            q = q.filter(stmt.inferred == False) # noqa

        q = q.order_by(stmt.subject.asc())
        return q

    def _collect(self, q):
        statements = []
        subject = None
        for stmt in q:
            if subject is not None and stmt.subject != subject:
                yield Entity(self._dataset,
                             id=subject,
                             statements=statements)
                statements = []
            subject = stmt.subject
            statements.append(stmt)
        if len(statements) and subject is not None:
            yield Entity(self._dataset,
                         id=subject,
                         statements=statements)

    def by_id(self, id):
        for entity in self._collect(self._query(id=id)):
            return entity

    def count(self):
        return self._sub_query(paginate=False).count()

    def __len__(self):
        return self.count()

    def __iter__(self):
        sq = self._sub_query()
        for entity in self._collect(self._query(sq=sq)):
            yield entity
