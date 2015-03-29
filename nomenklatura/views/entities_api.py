import json

from flask import Blueprint, request, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura import authz
from nomenklatura.model import Entity, Dataset, Context
from nomenklatura.query import execute_query, EntityQuery
from nomenklatura.processing import process_updates

blueprint = Blueprint('entities', __name__)


@blueprint.route('/datasets/<dataset>/entities', methods=['GET'])
def index(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    q = {}
    prefix = request.args.get('prefix', '')
    if len(prefix):
        q = {'label~=': prefix}
    q = EntityQuery(dataset, q)
    return jsonify(Pager(q, dataset=dataset.slug))


@blueprint.route('/datasets/<dataset>/query', methods=['GET', 'POST', 'PUT'])
def query(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    if request.method == 'GET':
        try:
            q = json.loads(request.args.get('q'))
        except (TypeError, ValueError) as e:
            data = {'status': 'error', 'message': 'Invalid query: %s' % unicode(e)}
            return jsonify(data, status=400)
    else:
        q = request_data()
    return jsonify(execute_query(dataset, q))


@blueprint.route('/datasets/<dataset>/entities', methods=['POST'])
def create(dataset):
    data = request_data()
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = Context.create(dataset, current_user, {})
    entity = Entity.create(dataset, data, context)
    db.session.commit()
    process_updates.delay(dataset.slug, entity_id=entity.id)
    return redirect(url_for('.view', dataset=dataset.slug, id=entity.id))


@blueprint.route('/datasets/<dataset>/entities/<id>', methods=['GET'])
def view(dataset, id):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    entity = obj_or_404(EntityQuery.by_id(dataset, id))
    return jsonify(entity)


@blueprint.route('/datasets/<dataset>/entities/<id>', methods=['POST'])
def update(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    entity = obj_or_404(EntityQuery.by_id(dataset, id))
    context = Context.create(dataset, current_user, {})
    entity.update(request_data(), context)
    db.session.commit()
    process_updates.delay(dataset.slug, entity_id=entity.id)
    return redirect(url_for('.view', dataset=dataset.slug, id=entity.id))
