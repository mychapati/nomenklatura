import time

from nomenklatura.query.parser import QueryNode
from nomenklatura.query.builder import QueryBuilder
from nomenklatura.query.entity import EntityQuery  # noqa


def execute_query(dataset, q):
    qb = QueryBuilder(dataset, None, QueryNode(None, None, q))
    t = time.time()
    result = qb.query()
    duration = (time.time() - t) * 1000
    return {
        'status': 'ok',
        'query': qb.node.to_dict(),
        'result': result,
        'time': duration
    }
