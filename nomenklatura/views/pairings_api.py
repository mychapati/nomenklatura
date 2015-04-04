from flask import Blueprint, request
from flask.ext.login import current_user
from apikit import jsonify, request_data, obj_or_404

from nomenklatura.views import authz
from nomenklatura.core import db
from nomenklatura.model import Pairing
from nomenklatura.query import EntityQuery
from nomenklatura.processing import request_pairing, generate_pairings


blueprint = Blueprint('pairing', __name__)


@blueprint.route('/pairings/next', methods=['GET'])
def load_next():
    authz.require(authz.system_edit())
    next = request_pairing(exclude=request.args.getlist('exclude'))
    db.session.commit()
    if next is None:
        return jsonify({'status': 'done'})
    return jsonify({
        'status': 'next',
        'next': next.id
    })


@blueprint.route('/pairings/<id>', methods=['GET'])
def view(id):
    authz.require(authz.system_edit())
    pairing = obj_or_404(Pairing.by_id(id))
    return jsonify({
        'status': 'ok',
        'left': EntityQuery.by_id(pairing.left_id),
        'right': EntityQuery.by_id(pairing.right_id),
        'pairing': pairing
    })


@blueprint.route('/pairings', methods=['POST', 'PUT'])
def store():
    authz.require(authz.system_edit())
    pairing = Pairing.update(request_data(), current_user)
    pairing.apply()
    db.session.commit()
    generate_pairings.delay()
    return jsonify(pairing)
