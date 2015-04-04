import copy

from sqlalchemy.orm import aliased, joinedload

from nomenklatura.core import db
from nomenklatura.model.statement import Statement
from nomenklatura.query.parser import QueryNode
from nomenklatura.query.builder import QueryBuilder
from nomenklatura.model.entity import Entity


class EntityQuery(object):

    def __init__(self, query=None, limit=None, offset=None):
        self.query = query or {}
        self._limit = limit
        self._offset = offset
        self._count = None

    def clone(self, query, **kw):
        query = copy.deepcopy(query)
        return EntityQuery(query=query,
                           limit=kw.get('limit', self._limit),
                           offset=kw.get('offset', self._offset))

    def limit(self, n):
        return self.clone(self.query, limit=n)

    def offset(self, n):
        return self.clone(self.query, offset=n)

    def _sub_query(self, query):
        qn = QueryNode(None, None, [query])
        qb = QueryBuilder(None, qn)
        return qn, qb.filter_query()

    def _main_query(self, query):
        stmt = aliased(Statement)
        qn, sq = self._sub_query(query)
        ssq = sq.subquery()
        q = db.session.query(stmt)
        q = q.options(joinedload(stmt.context))
        q = q.filter(stmt.subject == ssq.c.subject)
        q = q.order_by(ssq.c.subject)
        q = q.order_by(stmt.created_at.desc())
        return qn, q

    def _entities(self, query):
        statements = []
        subject = None
        qn, results = self._main_query(query)
        for stmt in results:
            stmt.assume_contexts = qn.assumed
            if subject is not None and stmt.subject != subject:
                yield Entity(id=subject, statements=statements,
                             assume_contexts=qn.assumed)
                statements = []
            subject = stmt.subject
            statements.append(stmt)
        if len(statements) and subject is not None:
            yield Entity(id=subject, statements=statements,
                         assume_contexts=qn.assumed)

    @classmethod
    def by_id(cls, id):
        return cls({'id': id, 'limit': 1}).first()

    def first(self):
        for entity in self:
            return entity

    def __len__(self):
        if self._count is None:
            query = copy.deepcopy(self.query)
            query['limit'] = None
            _, q = self._sub_query(query)
            self._count = q.count()
        return self._count

    def __iter__(self):
        for entity in self._entities(self.query):
            yield entity
