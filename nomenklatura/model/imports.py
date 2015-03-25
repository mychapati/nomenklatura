import logging

from loadkit.types.table import Table
from loadkit.operators.table import TableExtractOperator

from nomenklatura.core import db, archive, celery
from nomenklatura.model.context import Context

log = logging.getLogger(__name__)
COLLECTION = 'imports'


def get_package(dataset):
    coll = archive.get(COLLECTION)
    return coll.get(dataset.slug)


def get_table(context):
    package = get_package(context.dataset)
    source = package.get_resource(context.resource_name)
    target = Table(package, source.name + '.json')
    return source, target


def store_upload(dataset, file, filename, user):
    package = get_package(dataset)
    meta = {'source_file': filename}
    source = package.ingest(file, meta=meta, overwrite=False)
    ctx = {
        'active': False,
        'resource_name': source.path,
        'source_url': source.url
    }
    context = Context.create(dataset, user, ctx)
    db.session.add(context)
    return context


@celery.task
def analyze_upload(context_id):
    context = Context.by_id(context_id)
    if not context.resource_name:
        log.warning("No resource associated with context: %r", context)
        return
    source, target = get_table(context)
    if not source.exists():
        log.warning("Source data does not exist: %r", context.resource_name)
        return
    operator = TableExtractOperator(None, 'temp', {})
    operator.transform(source, target)
