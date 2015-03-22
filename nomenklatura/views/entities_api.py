from flask import Blueprint, request, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, arg_bool, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura.views.common import csvify, dataset_filename
from nomenklatura import authz
from nomenklatura.model import Entity, Dataset, Context

section = Blueprint('entities', __name__)


@section.route('/datasets/<dataset>/entities', methods=['GET'])
def index(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    q = dataset.entities
    # filter_name = request.args.get('filter_name', '')
    # if len(filter_name):
    #    query = '%' + filter_name + '%'
    #    entities = entities.filter(Entity.name.ilike(query))

    # TODO, other filters.
    format = request.args.get('format', 'json').lower().strip()
    if format == 'csv':
        res = csvify(q)
    else:
        res = jsonify(Pager(q, dataset=dataset.slug))

    if arg_bool('download'):
        fn = dataset_filename(dataset or 'all', format)
        res.headers['Content-Disposition'] = 'attachment; filename=' + fn
    return res


@section.route('/datasets/<dataset>/entities', methods=['POST'])
def create(dataset):
    data = request_data()
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    authz.require(authz.dataset_edit(dataset.slug))
    context = Context.create_generic(dataset, current_user)
    entity = Entity.create(dataset, data, context)
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.slug, id=entity.id))


@section.route('/datasets/<dataset>/entities/<id>', methods=['GET'])
def view(dataset, id):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    entity = obj_or_404(dataset.entities.by_id(id))
    return jsonify(entity)


@section.route('/datasets/<dataset>/entities/<id>/aliases', methods=['GET'])
def aliases(dataset, id):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    entity = obj_or_404(dataset.entities.by_id(id))
    print "XXXXX"
    # pager = Pager(entity.aliases, dataset=dataset.slug, id=id)
    # return jsonify(pager.to_dict())
    return jsonify({})


@section.route('/datasets/<dataset>/entities/<id>', methods=['POST'])
def update(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    entity = obj_or_404(dataset.entities.by_id(id))
    context = Context.create_generic(dataset, current_user)
    entity.update(request_data(), context)
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.slug, id=entity.id))
