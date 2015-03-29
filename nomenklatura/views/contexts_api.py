from flask import Blueprint, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404, arg_bool

from nomenklatura.core import db, url_for
from nomenklatura import authz
from nomenklatura.model import Dataset, Context
from nomenklatura.processing import process_updates

blueprint = Blueprint('contexts', __name__)


@blueprint.route('/datasets/<dataset>/contexts', methods=['GET'])
def index(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    q = dataset.contexts
    if arg_bool('imports'):
        q = q.filter(Context.resource_name != None) # noqa
    q = q.order_by(Context.updated_at.desc())
    return jsonify(Pager(q, dataset=dataset.slug))


@blueprint.route('/datasets/<dataset>/contexts', methods=['POST'])
def create(dataset):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = Context.create(dataset, current_user, request_data())
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.slug, id=context.id))


@blueprint.route('/datasets/<dataset>/contexts/<id>', methods=['GET'])
def view(dataset, id):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = obj_or_404(Context.by_id(id, dataset=dataset))
    return jsonify(context)


@blueprint.route('/datasets/<dataset>/contexts/<id>', methods=['POST'])
def update(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = obj_or_404(Context.by_id(id, dataset=dataset))
    context.update(request_data())
    db.session.commit()
    process_updates.delay(dataset.slug)
    return redirect(url_for('.view', dataset=dataset.slug, id=context.id))
