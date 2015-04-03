import logging
import time
import random

import dedupe

from nomenklatura.core import db, celery
from nomenklatura.schema import all_attributes
from nomenklatura.model import Pairing, Lock
from nomenklatura.query import EntityQuery, execute_query
from nomenklatura.query import same_as

KEEP_SIZE = 20
LOCK_DEDUPE = 'deduper:dedupe'
LOCK_GENERATE = 'deduper:generate'
log = logging.getLogger(__name__)


def make_fields():
    fields = []
    for attr in all_attributes():
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


def query_pairings(decided):
    q = db.session.query(Pairing)
    q = q.filter(Pairing.decided == decided) # noqa
    return q


def make_data(fields):
    data = {}
    q = {'limit': None}
    for e in EntityQuery(q):
        ent = {}
        for field in fields:
            name = field.get('field')
            ent[name] = e.get(name)
            if isinstance(ent[name], list):
                ent[name] = tuple([unicode(v) or '' for v in ent[name]])
            else:
                ent[name] = unicode(ent[name]) or ''
        data[e.id] = ent
    return data


def make_pairs(data):
    pairs = {'match': [], 'distinct': []}
    for pairing in query_pairings(True):
        if pairing.left_id not in data or pairing.right_id not in data:
            continue
        pair = (data.get(pairing.left_id), data.get(pairing.right_id))
        if pairing.decision is True:
            pairs['match'].append(pair)
        if pairing.decision is False:
            pairs['distinct'].append(pair)
    return pairs


@celery.task
def dedupe_generate_pairings(threshold=100):
    # do this only on full moon.
    num = query_pairings(True).count()
    log.info('Triggered dedupe, with %s pairings of training data', num)
    if num > threshold and num % threshold == 0:
        return
    time.sleep(random.uniform(0, 4))

    try:
        if not Lock.acquire(LOCK_DEDUPE):
            return

        log.info("Dedupe to generate pairings candidates")
        fields = make_fields()
        data = make_data(fields)
        pairs = make_pairs(data)

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
            score = ((s1 + s2) / 2.0) * 100.0
            matches.append((e1, e2, score))

        matches = sorted(matches, key=lambda (e, a, s): s, reverse=True)
        for (left_id, right_id, score) in matches:
            if score < 50:
                continue
            if not same_as.match(left_id, right_id):
                Pairing.update({'left_id': left_id, 'right_id': right_id},
                               None, score=score)
                db.session.commit()
    finally:
        Lock.release(LOCK_DEDUPE)


@celery.task
def generate_pairings(threshold=100):
    time.sleep(random.uniform(0, 4))
    dedupe_generate_pairings.delay(threshold=threshold)
    try:
        if not Lock.acquire(LOCK_GENERATE):
            return

        while query_pairings(False).count() <= KEEP_SIZE:
            generate_best_random_pairing()
    finally:
        Lock.release(LOCK_GENERATE)


def generate_random_pairing():
    query = {
        'label': None,
        'sort': 'random',
        'same_as': {'optional': 'forbidden'}
    }
    ent = execute_query(query).get('result')
    ent_id = ent.get('id')
    avoid = same_as.expand(ent_id)
    avoid.update(Pairing.existing(ent_id))
    q = {
        'id|!=': list(avoid),
        'label%=': ent.get('label')
    }
    for res in execute_query([q]).get('result'):
        return (res.get('id'), ent_id, res.get('score'))


def generate_best_random_pairing(num_rounds=10, cutoff=None):
    best_pair = None
    best_score = 0
    pairing = None
    for i in range(num_rounds):
        random_pairing = generate_random_pairing()
        if random_pairing is None:
            return
        left_id, right_id, score = random_pairing
        if cutoff is not None and score >= cutoff:
            pairing = Pairing.update({
                'left_id': left_id,
                'right_id': right_id
            }, None, score=score)
            break
        if score > best_score:
            best_score = score
            best_pair = (left_id, right_id)

    log.info('Generated best match, %r -> score %s', best_pair, best_score)
    if pairing is None and best_pair is not None:
        pairing = Pairing.update({
            'left_id': best_pair[0],
            'right_id': best_pair[1]
        }, None, score=best_score)
    db.session.commit()
    return pairing


def request_pairing(num_rounds=10, cutoff=95, exclude=None):
    q = Pairing.all()
    q = q.filter_by(decided=False)
    if exclude is not None:
        q = q.filter(~Pairing.id.in_(exclude))
    q = q.order_by(Pairing.score.desc())

    next_ = q.first()
    if next_ is not None:
        return next_

    next_ = generate_best_random_pairing(num_rounds=num_rounds,
                                         cutoff=cutoff)
    generate_pairings.delay()
    return next_
