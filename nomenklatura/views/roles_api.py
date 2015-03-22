from flask import Blueprint
from apikit import jsonify, request_data, obj_or_404

from nomenklatura import authz
from nomenklatura.core import db
from nomenklatura.model import Role, Dataset

blueprint = Blueprint('roles', __name__)


@blueprint.route('/datasets/<dataset>/roles', methods=['GET'])
def index(dataset):
    authz.require(authz.dataset_read(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    q = Role.all()
    q = q.filter(Role.dataset == dataset)
    return jsonify({'results': q.all(), 'total': q.count()})


@blueprint.route('/datasets/<dataset>/roles', methods=['POST'])
def update(dataset):
    authz.require(authz.dataset_manage(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    role = Role.update(request_data(), dataset)
    db.session.commit()
    return jsonify(role)
