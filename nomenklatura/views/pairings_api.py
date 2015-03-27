from flask import Blueprint, request
from flask.ext.login import current_user
from apikit import jsonify, obj_or_404, request_data

from nomenklatura import authz
from nomenklatura.core import db
from nomenklatura.model import Dataset, Pairing


blueprint = Blueprint('pairing', __name__)


@blueprint.route('/datasets/<dataset>/pairings', methods=['GET'])
def load(dataset):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    next = Pairing.next(dataset, exclude=request.args.get('exclude'))
    db.session.commit()
    if next is None:
        return {'status': 'done'}
    return jsonify(next)


@blueprint.route('/datasets/<dataset>/pairings', methods=['POST', 'PUT'])
def store(dataset):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    pairing = Pairing.update(request_data(), dataset, current_user)
    db.session.commit()
    return jsonify(pairing)
