from normality import normalize
from sqlalchemy import exists, and_, func
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.sql.expression import literal_column

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


class SubjectFilter(Filter):

    def __init__(self, subjects):
        self.subjects = subjects

    def apply(self, dataset, stmt, q):
        if len(self.subjects) == 1:
            return q.filter(stmt.subject == self.subjects[0])
        else:
            return q.filter(stmt.subject.in_(self.subjects))


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


class Levenshtein(LabelFilter):

    def apply(self, dataset, stmt, q):
        l_stmt, q = self.fields(stmt, q)
        value = normalize(self.value)[:254]
        field = func.left(l_stmt.normalized, 254)

        # calculate the difference percentage
        rel = func.greatest(max(float(len(self.value)), 1.0),
                            func.length(l_stmt.normalized))
        distance = func.levenshtein(field, value)
        score = ((rel - distance) / rel) * 100.0
        score = func.max(score).label('score')

        q = q.add_column(score)
        q = q.having(score >= 1)
        q = q.order_by(score.desc())
        return q


class EntityQuery(object):

    def __init__(self, dataset=None, limit=None, offset=None, filters=None):
        self._dataset = dataset
        self._limit = limit
        self._offset = offset
        self._filters = filters or []
        self._count = None

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

    def levenshtein(self, value, aliases=True):
        return self.filter(Levenshtein(value, aliases=aliases))

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

        q = q.group_by(subj)
        # q = q.distinct()
        if paginate:
            if self._limit is not None:
                q = q.limit(self._limit)
            if self._offset is not None:
                q = q.offset(self._offset)

        return q

    def _query(self, sq):
        stmt = aliased(Statement, name='stmt')
        ssq = sq.subquery()
        q = db.session.query(stmt)
        q = q.options(joinedload(stmt.context))
        q = q.filter(stmt.subject == ssq.c.subject)
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

    def first(self):
        q = self.limit(1)
        for res in q:
            return res

    def by_id(self, id):
        q = self.filter(SubjectFilter([id]))
        return q.first()

    def scored(self):
        sq = self._sub_query()
        results = sq.all()

        entity_ids = [r.subject for r in results]
        q = self._dataset.entities.filter(SubjectFilter(entity_ids))
        entities = list(q)

        for row in results:
            for ent in entities:
                if ent.id == row.subject:
                    yield int(row.score), ent

    def count(self):
        if self._count is None:
            self._count = self._sub_query(paginate=False).count()
        return self._count

    def __len__(self):
        return self.count()

    def __iter__(self):
        sq = self._sub_query()
        for res in self._collect(self._query(sq=sq)):
            yield res
