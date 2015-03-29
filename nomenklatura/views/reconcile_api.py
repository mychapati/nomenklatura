import json
import logging

from flask import Blueprint, request
from apikit import jsonify, get_limit, obj_or_404
from werkzeug.exceptions import BadRequest

from nomenklatura import authz
from nomenklatura.core import url_for
from nomenklatura.schema import attributes, types
from nomenklatura.model import Dataset
from nomenklatura.query import execute_query


blueprint = Blueprint('reconcile_api', __name__)
log = logging.getLogger(__name__)


def entity_ui(dataset, id):
    domain = url_for('index').strip('/')
    return '%s/datasets/%s/entities/%s' % (domain, dataset.slug, id)


def query_types(types_):
    queried = set()
    for type_name in types_:
        if type_name is None:
            continue
        if '/' in type_name:
            _, type_name = type_name.rsplit('/', 1)
        queried.add(type_name)
    return queried if len(queried) else None


def reconcile_index(dataset):
    domain = url_for('index').strip('/')
    meta = {
        'name': dataset.label,
        'identifierSpace': 'http://rdf.freebase.com/ns/type.object.id',
        'schemaSpace': 'http://rdf.freebase.com/ns/type.object.id',
        'view': {'url': entity_ui(dataset, '{{id}}')},
        'preview': {
            'url': entity_ui(dataset, '{{id}}') + '?preview=true',
            'width': 600,
            'height': 300
        },
        'suggest': {
            'entity': {
                'service_url': domain,
                'service_path': '/api/2/datasets/' + dataset.slug + '/suggest'
            },
            'type': {
                'service_url': domain,
                'service_path': '/api/2/reconcile/type'
            },
            'property': {
                'service_url': domain,
                'service_path': '/api/2/reconcile/property'
            }
        },
        'defaultTypes': [t.to_freebase_type() for t in types]
    }
    return jsonify(meta)


def reconcile_op(dataset, query):
    log.info("Reconciling in %s: %r", dataset.slug, query)

    # properties = []
    # if 'properties' in query:
    #     for p in query.get('properties'):
    #         properties.append((p.get('pid'), p.get('v')))

    q = {
        'label%=': query.get('query', ''),
        'type': query_types([query.get('type')]),
        'limit': get_limit(default=5),
        'same_as': {'optional': 'forbidden'}
    }

    results = []
    for entity in execute_query(dataset, [q]).get('result'):
        type_ = types[entity.get('type')].to_freebase_type()
        results.append({
            'id': entity.get('id'),
            'name': entity.get('label'),
            'score': entity.get('score'),
            'type': [type_],
            'uri': entity_ui(dataset, entity.get('id')),
            'match': False
        })

    return {
        'result': results,
        'num': len(results)
    }


@blueprint.route('/datasets/<dataset>/reconcile', methods=['GET', 'POST'])
def reconcile(dataset):
    """
    Reconciliation API, emulates Google Refine API. See:
    http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi
    """
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    # TODO: Add proper support for types and namespacing.
    data = request.args.copy()
    data.update(request.form.copy())

    if 'query' in data:
        # single
        q = data.get('query')
        if q.startswith('{'):
            try:
                q = json.loads(q)
            except ValueError:
                raise BadRequest()
        else:
            q = data
        return jsonify(reconcile_op(dataset, q))
    elif 'queries' in data:
        # multiple requests in one query
        qs = data.get('queries')
        try:
            qs = json.loads(qs)
        except ValueError:
            raise BadRequest()
        queries = {}
        for k, q in qs.items():
            queries[k] = reconcile_op(dataset, q)
        return jsonify(queries)
    else:
        return reconcile_index(dataset)


@blueprint.route('/datasets/<dataset>/suggest', methods=['GET', 'POST'])
def suggest_entity(dataset):
    """
    Suggest API, emulates Google Refine API. See:
    https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API
    """
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    prefix = request.args.get('prefix', '')
    log.info("Suggesting entities in %s: %r", dataset.slug, prefix)

    q = {
        'label~=': prefix,
        'type': query_types(request.args.getlist('type')),
        'limit': get_limit(default=5),
        'same_as': {'optional': 'forbidden'}
    }

    matches = []
    for entity in execute_query(dataset, [q]).get('result'):
        type_ = types[entity.get('type')].to_freebase_type()
        matches.append({
            'id': entity.get('id'),
            'name': entity.get('label'),
            'n:type': type_,
            'type': [type_],
            'uri': entity_ui(dataset, entity.get('id'))
        })

    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })


@blueprint.route('/reconcile/property', methods=['GET', 'POST'])
def suggest_property():
    prefix = request.args.get('prefix', '')
    log.info("Suggesting property names: %r", prefix)

    matches = []
    for attribute in list(attributes.suggest(prefix))[:5]:
        matches.append({
            'name': attribute.label,
            'n:type': {
                'id': '/properties/property',
                'name': 'Property'
            },
            'id': attribute.name
        })
    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })


@blueprint.route('/reconcile/type', methods=['GET', 'POST'])
def suggest_type():
    prefix = request.args.get('prefix', '')
    log.info("Suggesting types: %r", prefix)

    matches = []
    for type_ in list(types.suggest(prefix))[:5]:
        matches.append(type_.to_freebase_type())
    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })
