import json
import logging

from flask import Blueprint, request
from apikit import jsonify, get_limit
from werkzeug.exceptions import BadRequest

from nomenklatura.core import url_for, app_title
from nomenklatura.views import authz
from nomenklatura.schema import qualified, types
from nomenklatura.query import execute_query


blueprint = Blueprint('reconcile_api', __name__)
log = logging.getLogger(__name__)


def entity_ui(id):
    domain = url_for('index').strip('/')
    return '%s/entities/%s' % (domain, id)


def query_types(types_):
    queried = set()
    for type_name in types_:
        if type_name is None:
            continue
        if '/' in type_name:
            _, type_name = type_name.rsplit('/', 1)
        queried.add(type_name)
    return list(queried) if len(queried) else None


def reconcile_index():
    domain = url_for('index').strip('/')
    meta = {
        'name': app_title,
        'identifierSpace': 'http://rdf.freebase.com/ns/type.object.id',
        'schemaSpace': 'http://rdf.freebase.com/ns/type.object.id',
        'view': {'url': entity_ui('{{id}}')},
        'preview': {
            'url': entity_ui('{{id}}') + '?preview=true',
            'width': 600,
            'height': 300
        },
        'suggest': {
            'entity': {
                'service_url': domain,
                'service_path': '/api/2/suggest'
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
        'defaultTypes': [t.to_freebase_type() for t in types if not t.abstract]
    }
    return jsonify(meta)


def reconcile_op(query):
    log.info("Reconciling: %r", query)

    q = {
        'label%=': query.get('query', ''),
        'type': query_types([query.get('type')]),
        'limit': get_limit(default=5),
        'same_as': {'optional': 'forbidden'}
    }
    for p in query.get('properties', []):
        q[p.get('pid')] = p.get('v')

    results = []
    for entity in execute_query([q]).get('result'):
        type_ = entity.get('type')
        type_ = type_ if isinstance(type_, (list, set, tuple)) else type_
        type_ = types[type_].to_freebase_type()
        results.append({
            'id': entity.get('id'),
            'name': entity.get('label'),
            'score': entity.get('score'),
            'type': [type_],
            'uri': entity_ui(entity.get('id')),
            'match': False
        })

    best = results[0] if len(results) else None
    log.info("Returning %s candidates, best: %r", len(results), best)
    return {
        'result': results,
        'num': len(results)
    }


@blueprint.route('/reconcile', methods=['GET', 'POST'])
def reconcile():
    """
    Reconciliation API, emulates Google Refine API. See:
    http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi
    """
    authz.require(authz.system_read())
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
        return jsonify(reconcile_op(q))
    elif 'queries' in data:
        # multiple requests in one query
        qs = data.get('queries')
        try:
            qs = json.loads(qs)
        except ValueError:
            raise BadRequest()
        queries = {}
        for k, q in qs.items():
            queries[k] = reconcile_op(q)
        return jsonify(queries)
    else:
        return reconcile_index()


@blueprint.route('/suggest', methods=['GET', 'POST'])
def suggest_entity():
    """
    Suggest API, emulates Google Refine API. See:
    https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API
    """
    authz.require(authz.system_read())
    prefix = request.args.get('prefix', '')

    q = {
        'label~=': prefix,
        'type': query_types(request.args.getlist('type')),
        'limit': get_limit(default=5),
        'same_as': {'optional': 'forbidden'}
    }

    matches = []
    for entity in execute_query([q]).get('result'):
        type_ = types[entity.get('type')].to_freebase_type()
        matches.append({
            'id': entity.get('id'),
            'name': entity.get('label'),
            'n:type': type_,
            'type': [type_],
            'uri': entity_ui(entity.get('id'))
        })

    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })


@blueprint.route('/reconcile/property', methods=['GET', 'POST'])
def suggest_property():
    authz.require(authz.system_read())
    prefix = request.args.get('prefix', '')
    matches = []
    for qname, attribute in qualified.items():
        if attribute.match_prefix(prefix):
            matches.append({
                'name': attribute.label,
                'n:type': {
                    'id': '/properties/property',
                    'name': 'Property'
                },
                'id': qname
            })
    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })


@blueprint.route('/reconcile/type', methods=['GET', 'POST'])
def suggest_type():
    authz.require(authz.system_read())
    prefix = request.args.get('prefix', '')
    matches = []
    for type_ in types:
        if type_.match_prefix(prefix):
            matches.append(type_.to_freebase_type())
    return jsonify({
        "code": "/api/status/ok",
        "status": "200 OK",
        "prefix": prefix,
        "result": matches
    })
