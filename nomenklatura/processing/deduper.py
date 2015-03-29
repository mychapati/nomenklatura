import logging

import dedupe

from nomenklatura.core import db, celery
from nomenklatura.schema import attributes
from nomenklatura.model.dataset import Dataset
from nomenklatura.model.pairing import Pairing

log = logging.getLogger(__name__)


def make_fields():
    fields = []
    for attr in attributes:
        if attr.data_type in ['string', 'text']:
            fields.append({
                'field': attr.name,
                'type': 'Set' if attr.many else 'String',
                'has missing': True
            })
        if attr.data_type in ['type']:
            fields.append({
                'field': attr.name,
                'type': 'Exact'
            })
    return fields


def query_pairings(dataset):
    q = db.session.query(Pairing)
    q = q.filter(Pairing.dataset == dataset)
    q = q.filter(Pairing.decided == True) # noqa
    return q


def make_data(dataset, fields):
    data = {}
    for e in dataset.entities:
        ent = {}
        for field in fields:
            name = field.get('field')
            ent[name] = e.get(name)
            if isinstance(ent[name], list):
                ent[name] = tuple([v or '' for v in ent[name]])
            else:
                ent[name] = ent[name] or ''
        data[e.id] = ent
    return data


def make_pairs(dataset, data):
    pairs = {'match': [], 'distinct': []}
    for pairing in query_pairings(dataset):
        pair = (data.get(pairing.left_id), data.get(pairing.right_id))
        if pairing.decision is True:
            pairs['match'].append(pair)
        if pairing.decision is False:
            pairs['distinct'].append(pair)
    return pairs


@celery.task
def generate_pairings(slug, threshold=15):
    dataset = Dataset.by_slug(slug)
    num = query_pairings(dataset).count()

    # do this only on full moon.
    if num < threshold or num % threshold != 0:
        return

    log.info("Dedupe to generate pairings candidates: %s", slug)
    fields = make_fields()
    data = make_data(dataset, fields)
    pairs = make_pairs(dataset, data)

    deduper = dedupe.Dedupe(fields)
    deduper.sample(data)
    deduper.markPairs(pairs)
    deduper.train()

    matches = []
    for match in deduper.match(data):
        scored = sorted(zip(match[0], match[1]),
                        key=lambda (id, s): s, reverse=True)
        scored = list(scored)[:2]
        (e1, s1), (e2, s2) = scored
        score = (s1 + s2) / 2.0
        matches.append((e1, e2, score))

    matches = sorted(matches, key=lambda (e, a, s): s, reverse=True)
    for (left_id, right_id, score) in matches[:30]:
        Pairing.update({'left_id': left_id, 'right_id': right_id},
                       dataset, None, score=score)
    db.session.commit()
