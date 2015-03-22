from flask import Blueprint, request, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, arg_bool, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura.views.common import csvify, dataset_filename
from nomenklatura import authz
from nomenklatura.model import Entity, Dataset
from nomenklatura.model.query import EntityQuery

section = Blueprint('entities', __name__)


@section.route('/entities', methods=['GET'])
def index():
    q = EntityQuery()
    dataset = request.args.get('dataset')
    if dataset is not None:
        dataset = obj_or_404(Dataset.by_slug(dataset))
        q = q.filter_dataset(dataset)

    # filter_name = request.args.get('filter_name', '')
    # if len(filter_name):
    #    query = '%' + filter_name + '%'
    #    entities = entities.filter(Entity.name.ilike(query))

    # TODO, other filters.

    format = request.args.get('format', 'json').lower().strip()
    if format == 'csv':
        res = csvify(q)
    else:
        res = jsonify(Pager(q))

    if arg_bool('download'):
        fn = dataset_filename(dataset or 'all', format)
        res.headers['Content-Disposition'] = 'attachment; filename=' + fn
    return res


@section.route('/entities', methods=['POST'])
def create():
    data = request_data()
    dataset = Dataset.from_form(data)
    authz.require(authz.dataset_edit(dataset.name))
    entity = Entity.create(dataset, data, current_user)
    db.session.commit()
    return redirect(url_for('.view', id=entity.id))


@section.route('/entities/<int:id>', methods=['GET'])
def view(id):
    entity = obj_or_404(Entity.by_id(id))
    return jsonify(entity)


@section.route('/datasets/<dataset>/find', methods=['GET'])
def by_name(dataset):
    dataset = obj_or_404(Dataset.by_slug(dataset))
    name = request.args.get('name')
    entity = obj_or_404(Entity.by_name(dataset, name))
    return jsonify(entity)


@section.route('/entities/<int:id>/aliases', methods=['GET'])
def aliases(id):
    entity = obj_or_404(Entity.by_id(id))
    pager = Pager(entity.aliases, id=id)
    return jsonify(pager.to_dict())


@section.route('/entities/<id>', methods=['POST'])
def update(id):
    entity = obj_or_404(Entity.by_id(id))
    authz.require(authz.dataset_edit(entity.dataset.name))
    entity.update(request_data(), current_user)
    db.session.commit()
    return redirect(url_for('.view', id=entity.id))