from nomenklatura.core import celery as app
from nomenklatura.processing import deduper, inference


@app.task
def process_updates(slug, entity_id=None, statement_id=None):
    deduper.generate_pairings.delay(slug)
    inference.generate_inferred.delay(slug)
