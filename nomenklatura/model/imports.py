import logging

from loadkit.types.table import Table
from loadkit.operators.table import TableExtractOperator

from nomenklatura.core import db, archive, celery
from nomenklatura.model.context import Context
from nomenklatura.model.entity import Entity
from nomenklatura.model.schema import types, attributes

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


@celery.task
def load_upload(context_id):
    context = Context.by_id(context_id)
    if not context.resource_name or not context.resource_mapping:
        log.warning("No resource associated with context: %r", context)
        return
    source, table = get_table(context)
    for record in table.records():
        load_entity(context, context.resource_mapping, record)

    context.active = True
    db.session.commit()


def load_entity(context, mapping, record):
    type_ = types.get(mapping.get('type'))
    if type_ is None:
        log.warning("No type defined for entity in mapping: %r", mapping)
        return

    q = context.dataset.entities.filter_by(attributes.type, type_)
    has_key = False

    data = [(attributes.type, type_)]
    for attr in type_.attributes:
        if attr.name not in mapping or attr.name == 'type':
            continue
        attr_map = mapping[attr.name]
        if attr.data_type == 'entity':
            value = load_entity(context, attr_map, record)
        else:
            value = record.get(attr_map.get('field'))

        if attr_map.get('key'):
            has_key = True
            q = q.filter_by(attr, value)

        data.append((attr, value))

    entity = q.first() if has_key else None
    if entity is None:
        entity = Entity(context.dataset)

    for (attr, value) in data:
        entity.set(attr, value, context)

    log.info("Loaded entity: %r", entity)
    return entity
