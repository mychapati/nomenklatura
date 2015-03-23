from normality import normalize
from sqlalchemy import exists, and_
from sqlalchemy.orm import aliased, joinedload

from nomenklatura.core import db
from nomenklatura.model.schema import attributes
from nomenklatura.model.statement import Statement
from nomenklatura.model.context import Context
from nomenklatura.model.entity import Entity


class Filter(object):

    def _add_statement(self, main_stmt, q):
        stmt = aliased(Statement)
        ctx = aliased(Context)
        q = q.filter(main_stmt.subject == stmt.subject)
        q = q.filter(stmt.context_id == ctx.id)
        q = q.filter(ctx.active == True) # noqa
        return stmt, q


class ValueFilter(Filter):

    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

    def apply(self, dataset, stmt, q):
        conv = self.attribute.converter(dataset)
        t_stmt, q = self._add_statement(stmt, q)
        q = q.filter(t_stmt._attribute == unicode(self.attribute))
        q = q.filter(t_stmt._value == conv.serialize(self.value))
        return q


class SameAsFilter(Filter):

    def apply(self, dataset, stmt, q):
        same_as = aliased(Statement)
        return q.filter(~exists().where(and_(
            same_as._attribute == attributes.same_as.name,
            same_as.subject == stmt.subject
        )))


class LabelFilter(Filter):

    def __init__(self, value, aliases=True):
        self.value = value
        self.aliases = aliases

    def fields(self, stmt, q):
        l_stmt, q = self._add_statement(stmt, q)
        if self.aliases:
            attrs = [unicode(attributes.label), unicode(attributes.alias)]
            q = q.filter(l_stmt._attribute.in_(attrs))
        else:
            q = q.filter(l_stmt._attribute == unicode(attributes.label))
        return l_stmt, q

    def apply(self, dataset, stmt, q):
        conv = self.attribute.converter(dataset)
        l_stmt, q = self.fields(stmt, q)
        return q.filter(l_stmt._value == conv.serialize(self.value))


class PrefixFilter(LabelFilter):

    def apply(self, dataset, stmt, q):
        l_stmt, q = self.fields(stmt, q)
        value = '%s%%' % normalize(self.value)
        return q.filter(l_stmt.normalized.like(value))


class EntityQuery(object):

    def __init__(self, dataset=None, limit=None, offset=None, filters=None):
        self._dataset = dataset
        self._limit = limit
        self._offset = offset
        self._filters = filters or []

    def clone(self, **kw):
        return EntityQuery(dataset=kw.get('dataset', self._dataset),
                           limit=kw.get('limit', self._limit),
                           offset=kw.get('offset', self._offset),
                           filters=kw.get('filters', self._filters))

    def filter(self, filter):
        filters = self._filters + [filter]
        return self.clone(filters=filters)

    def filter_by(self, attribute, value):
        return self.filter(ValueFilter(attribute, value))

    def no_same_as(self):
        return self.filter(SameAsFilter())

    def filter_label(self, value, aliases=True):
        return self.filter(LabelFilter(value, aliases=aliases))

    def filter_prefix(self, value, aliases=True):
        return self.filter(PrefixFilter(value, aliases=aliases))

    def limit(self, n):
        return self.clone(limit=n)

    def offset(self, n):
        return self.clone(offset=n)

    def _sub_query(self, paginate=True):
        stmt = aliased(Statement)
        subj = stmt.subject.label('subject')
        q = db.session.query(subj)
        q = q.filter(stmt.dataset_id == self._dataset.id)

        for filter in self._filters:
            q = filter.apply(self._dataset, stmt, q)

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
        # if not self._same_as:
        #    q = q.filter(stmt.inferred == False) # noqa

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
