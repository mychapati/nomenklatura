import json

from flask import Blueprint, request, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura.views import authz
from nomenklatura.schema import attributes, types
from nomenklatura.model import Entity, Context
from nomenklatura.query import execute_query, EntityQuery

blueprint = Blueprint('entities', __name__)


@blueprint.route('/schema')
def schema():
    return jsonify({
        'attributes': attributes,
        'types': types
    })


@blueprint.route('/entities', methods=['GET'])
def index():
    authz.require(authz.system_read())
    q = {}
    prefix = request.args.get('prefix', '')
    if len(prefix):
        q = {'label~=': prefix}
    q = EntityQuery(q)
    return jsonify(Pager(q))


@blueprint.route('/query', methods=['GET', 'POST', 'PUT'])
def query():
    authz.require(authz.system_read())
    if request.method == 'GET':
        try:
            q = json.loads(request.args.get('q'))
        except (TypeError, ValueError) as e:
            data = {
                'status': 'error',
                'message': 'Invalid query: %s' % unicode(e)
            }
            return jsonify(data, status=400)
    else:
        q = request_data()
    return jsonify(execute_query(q))


@blueprint.route('/entities', methods=['POST'])
def create():
    authz.require(authz.system_edit())
    context = Context.create(current_user, {})
    entity = Entity.create(request_data(), context)
    db.session.commit()
    return redirect(url_for('.view', id=entity.id))


@blueprint.route('/entities/<id>', methods=['GET'])
def view(id):
    authz.require(authz.system_read())
    entity = obj_or_404(EntityQuery.by_id(id))
    return jsonify(entity)


@blueprint.route('/entities/<id>', methods=['POST'])
def update(id):
    authz.require(authz.system_edit())
    entity = obj_or_404(EntityQuery.by_id(id))
    context = Context.create(current_user, {})
    entity.update(request_data(), context)
    db.session.commit()
    return redirect(url_for('.view', id=entity.id))
