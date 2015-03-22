from sqlalchemy.orm import aliased, joinedload

from nomenklatura.core import db
from nomenklatura.model.statement import Statement
from nomenklatura.model.context import Context
from nomenklatura.model.entity import Entity


class EntityQuery(object):

    def __init__(self, dataset=None, limit=None, offset=None):
        self._dataset = dataset
        self._limit = limit
        self._offset = offset

    def clone(self, **kw):
        return EntityQuery(dataset=kw.get('dataset', self._dataset),
                           limit=kw.get('limit', self._limit),
                           offset=kw.get('offset', self._offset))

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

        # if self._dataset is not None:
        #     q = q.filter(stmt.dataset_id == self._dataset.id)

        if sq is not None:
            sq = sq.subquery()
            q = q.outerjoin(sq, stmt.subject == sq.c.subject)
        else:
            q = q.filter(stmt.subject == id)

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
