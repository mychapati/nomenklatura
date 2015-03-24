from flask import Blueprint, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404

from nomenklatura.core import db, url_for
from nomenklatura import authz
from nomenklatura.model import Dataset, Context

blueprint = Blueprint('contexts', __name__)


@blueprint.route('/datasets/<dataset>/contexts', methods=['GET'])
def index(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    return jsonify(Pager(dataset.contexts, dataset=dataset.slug))


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
    return redirect(url_for('.view', dataset=dataset.slug, id=context.id))
