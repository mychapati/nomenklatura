import json
import logging

from flask import Blueprint, request
from apikit import jsonify, get_limit, obj_or_404
from werkzeug.exceptions import BadRequest

from nomenklatura import authz
from nomenklatura.core import db, url_for
from nomenklatura.model.schema import attributes, types
from nomenklatura.model import Dataset

# from grano.logic.reconcile import find_matches


blueprint = Blueprint('reconcile_api', __name__)
log = logging.getLogger(__name__)


def reconcile_index(dataset):
    domain = url_for('index').strip('/')
    urlp = '%s/datasets/%s/entities/{{id}}' % (domain, dataset.slug)
    meta = {
        'name': dataset.label,
        'identifierSpace': 'http://rdf.freebase.com/ns/type.object.id',
        'schemaSpace': 'http://rdf.freebase.com/ns/type.object.id',
        'view': {'url': urlp},
        'preview': {
            'url': urlp + '?preview=true',
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
        'defaultTypes': []
    }

    for type_ in types:
        meta['defaultTypes'].append({
            'id': '/types/%s' % type_.name,
            'name': type_.label
        })
    return jsonify(meta)


def reconcile_op(dataset, query):
    log.info("Reconciling in %s: %r", dataset.slug, query)

    schemata = []
    if 'type' in query:
        schemata = query.get('type')
        if isinstance(schemata, basestring):
            schemata = [schemata]
        schemata = [s.rsplit('/', 1)[-1] for s in schemata]

    properties = []
    if 'properties' in query:
        for p in query.get('properties'):
            properties.append((p.get('pid'), p.get('v')))

    matches = find_matches(dataset, request.account,
                           query.get('query', ''),
                           schemata=schemata,
                           properties=properties)
    matches = matches.limit(get_limit(default=5))

    results = []
    for match in matches:
        data = {
            'name': match['entity']['name'].value,
            'score': match['score'],
            'type': [{
                'id': '/' + dataset.slug + '/' + match['entity'].schema.name,
                'name': match['entity'].schema.label
            }],
            'id': match['entity'].id,
            'uri': url_for('entities_api.view', id=match['entity'].id,
                           _external=True),
            'match': False  # match['score'] == 100
        }
        results.append(data)

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

    q = dataset.entities.no_same_as()
    q = q.filter_prefix(prefix)

    if 'type' in request.args:
        schema_name = request.args.get('type')
        if '/' in schema_name:
            _, schema_name = schema_name.rsplit('/', 1)
        q = q.filter_by(attributes.type, schema_name)

    q = q.limit(get_limit(default=5))

    matches = []
    for entity in q:
        data = {
            'id': entity.id,
            'name': entity.label,
            'uri': url_for('entities.view', dataset=dataset.slug, id=entity.id)
        }
        data_type = {'id': '/types/Undefined', 'name': 'Undefined'}
        if entity.type:
            data_type = {
                'id': '/types/%s' % entity.type.name,
                'name': entity.type.label
            }

        data['n:type'] = data_type
        data['type'] = [data_type]
        matches.append(data)

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
        matches.append({
            'name': type_.label,
            'id': '/types/%s' % type_.name
        })
    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })
