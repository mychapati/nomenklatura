import copy

from sqlalchemy.orm import aliased, joinedload

from nomenklatura.core import db
from nomenklatura.model.statement import Statement
from nomenklatura.query.parser import QueryNode # noqa
from nomenklatura.query.builder import QueryBuilder # noqa
from nomenklatura.model.entity import Entity


class EntityQuery(object):

    def __init__(self, dataset, query=None, limit=None, offset=None):
        self.dataset = dataset
        self.query = query or {}
        self._limit = limit
        self._offset = offset
        self._count = None

    def clone(self, query, **kw):
        query = copy.deepcopy(query)
        return EntityQuery(dataset=kw.get('dataset', self.dataset),
                           query=query,
                           limit=kw.get('limit', self._limit),
                           offset=kw.get('offset', self._offset))

    def limit(self, n):
        return self.clone(limit=n)

    def offset(self, n):
        return self.clone(offset=n)

    def _sub_query(self, query):
        qn = QueryNode(None, None, [query])
        qb = QueryBuilder(self.dataset, None, qn)
        return qb.filter_query()

    def _main_query(self, query):
        stmt = aliased(Statement)
        ssq = self._sub_query(query).subquery()
        q = db.session.query(stmt)
        q = q.options(joinedload(stmt.context))
        q = q.filter(stmt.subject == ssq.c.subject)
        q = q.order_by(ssq.c.subject)
        return q

    def _entities(self, query):
        statements = []
        subject = None
        for stmt in self._main_query(query):
            if subject is not None and stmt.subject != subject:
                yield Entity(self.dataset,
                             id=subject,
                             statements=statements)
                statements = []
            subject = stmt.subject
            statements.append(stmt)
        if len(statements) and subject is not None:
            yield Entity(self.dataset,
                         id=subject,
                         statements=statements)

    @classmethod
    def by_id(cls, dataset, id):
        for entity in cls(dataset, {'id': id, 'limit': 1}):
            return entity

    def __len__(self):
        if self._count is None:
            query = copy.deepcopy(self.query)
            query['limit'] = None
            self._count = self._sub_query(query).count()
        return self._count

    def __iter__(self):
        for entity in self._entities(self.query):
            yield entity
