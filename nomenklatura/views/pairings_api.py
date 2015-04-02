from flask import Blueprint, request
from flask.ext.login import current_user
from apikit import jsonify, request_data

from nomenklatura.views import authz
from nomenklatura.core import db
from nomenklatura.model import Pairing
from nomenklatura.query import EntityQuery
from nomenklatura.processing import request_pairing, generate_pairings


blueprint = Blueprint('pairing', __name__)


@blueprint.route('/pairings', methods=['GET'])
def load():
    authz.require(authz.system_edit())
    next = request_pairing(exclude=request.args.getlist('exclude'))
    db.session.commit()
    if next is None:
        return jsonify({'status': 'done'})
    return jsonify({
        'status': 'next',
        'left': EntityQuery.by_id(next.left_id),
        'right': EntityQuery.by_id(next.right_id),
        'pairing': next
    })


@blueprint.route('/pairings', methods=['POST', 'PUT'])
def store():
    authz.require(authz.system_edit())
    pairing = Pairing.update(request_data(), current_user)
    pairing.apply()
    db.session.commit()
    generate_pairings.delay()
    return jsonify(pairing)
