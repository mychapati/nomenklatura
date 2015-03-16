from normality import normalize
from sqlalchemy import func, select, and_

from nomenklatura.model.entity import Entity
from nomenklatura.core import db


class Matches(object):

    def __init__(self, q):
        self.lq = self.q = q

    def limit(self, l):
        self.lq = self.lq.limit(l)
        return self

    def offset(self, o):
        self.lq = self.lq.offset(o)
        return self

    def count(self):
        rp = db.engine.execute(self.q.alias('count').count())
        (count,) = rp.fetchone()
        return count

    def __iter__(self):
        rp = db.engine.execute(self.lq)
        rows = rp.fetchall()
        ids = [r[0] for r in rows]
        entities = Entity.id_map(ids)
        for (id, score) in rows:
            yield {'score': int(score), 'entity': entities.get(id)}


def find_matches(dataset, text, filter=None, exclude=None):
    entities = Entity.__table__
    match_text = normalize(text or '')[:254]

    # select text column and apply necesary transformations
    text_field = func.left(entities.c.normalized, 254)

    # calculate the difference percentage
    rel = func.greatest(max(len(match_text), 1), func.length(text_field))
    distance = func.levenshtein(text_field, match_text)
    score = func.greatest(0.0, ((rel - distance) / rel) * 100.0)
    score = func.max(score).label('score')

    # coalesce the canonical identifier
    id_ = func.coalesce(entities.c.canonical_id, entities.c.id).label('id')

    # apply filters
    filters = [entities.c.dataset_id == dataset.id,
               entities.c.invalid == False] # noqa
    if not dataset.match_aliases:
        filters.append(entities.c.canonical_id == None) # noqa
    if exclude is not None:
        filters.append(entities.c.id != exclude)
    if filter is not None:
        filters.append(text_field.ilike('%%%s%%' % filter))

    q = select([id_, score], and_(*filters), [entities],
               group_by=[id_], order_by=[score.desc()])
    return Matches(q)


def attribute_keys(dataset):
    entities = Entity.__table__
    col = func.distinct(func.skeys(entities.c.attributes)).label('keys')
    q = select([col], entities.c.dataset_id == dataset.id, [entities])
    rp = db.engine.execute(q)
    keys = set()
    for row in rp.fetchall():
        keys.add(row[0])
    return sorted(keys)
