from flask import Blueprint, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura import authz
from nomenklatura.model import Role, Dataset

blueprint = Blueprint('roles', __name__)


@blueprint.route('/datasets/<dataset>/roles', methods=['GET'])
def index(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    q = Role.all()
    q = q.filter(Role.dataset == dataset)
    pager = Pager(q, dataset=dataset.slug)
    return jsonify(pager.to_dict())


@blueprint.route('/datasets/<dataset>/roles', methods=['POST'])
def update(dataset):
    authz.require(authz.dataset_manage(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    role = None
    return jsonify(role)
