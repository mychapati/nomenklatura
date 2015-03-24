from flask import Blueprint, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura import authz
from nomenklatura.model import Dataset

blueprint = Blueprint('datasets', __name__)


@blueprint.route('/datasets', methods=['GET'])
def index():
    q = Dataset.all()
    q = q.filter(Dataset.slug.in_(authz.datasets('read')))
    pager = Pager(q)
    return jsonify(pager.to_dict())


@blueprint.route('/datasets', methods=['POST'])
def create():
    authz.require(authz.dataset_create())
    dataset = Dataset.create(request_data(), current_user)
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.slug))


@blueprint.route('/datasets/<dataset>', methods=['GET'])
def view(dataset):
    dataset = obj_or_404(Dataset.by_slug(dataset))
    return jsonify(dataset)


@blueprint.route('/datasets/<dataset>', methods=['POST'])
def update(dataset):
    authz.require(authz.dataset_manage(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    dataset.update(request_data())
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.slug))
