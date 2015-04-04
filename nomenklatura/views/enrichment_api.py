from flask import Blueprint
from flask.ext.login import current_user
from apikit import jsonify, request_data, obj_or_404

from nomenklatura.views import authz
from nomenklatura.core import db
from nomenklatura.model import Context
from nomenklatura.model.constants import PENDING, ACCEPTED
from nomenklatura.enrichment import get_spiders, enrich_entity


blueprint = Blueprint('enrichment', __name__)


@blueprint.route('/spiders', methods=['GET'])
def spiders():
    authz.require(authz.system_read())
    spiders = {}
    for name, spider in get_spiders().items():
        spiders[name] = {
            'name': name,
            'class': spider.__name__,
            'label': spider.PUBLISHER_LABEL,
            'url': spider.PUBLISHER_URL
        }
    return jsonify(spiders)


@blueprint.route('/enrichment', methods=['POST'])
def initiate():
    authz.require(authz.system_edit())
    root = request_data().get('root')
    if root is None:
        return jsonify({
            'status': 'error',
            'message': 'No root entity provided.'},
            status=400)
    enrich_entity.delay(root, request_data().get('spider'))
    return jsonify({'status': 'ok', 'root': root})


@blueprint.route('/enrichment/<root>/next', methods=['GET'])
def load_next(root):
    authz.require(authz.system_edit())
    q = Context.by_root(root)
    q = q.filter(Context.enrich_status == PENDING)
    q = q.order_by(Context.enrich_score.desc())
    context = q.first()
    if context is None:
        # TODO: spider status system
        return jsonify({'status': 'wait'})
    return jsonify({
        'status': 'next',
        'next': context.id
    })


@blueprint.route('/enrichment/<root>/<id>', methods=['GET'])
def view(root, id):
    authz.require(authz.system_edit())
    q = Context.by_root(root)
    q = q.filter(Context.id == id)
    context = obj_or_404(q.first())
    return jsonify({
        'status': 'ok',
        'context': context.to_dict(enrich=True),
        'statements': [s.to_dict(raw=True) for s in context.statements]
    })


@blueprint.route('/enrichment/<root>', methods=['POST', 'PUT'])
def store(root):
    authz.require(authz.system_edit())
    ctx_data = request_data()
    q = Context.by_root(root)
    q = q.filter(Context.id == ctx_data.get('id'))
    context = q.first()
    if context is None:
        return jsonify({'status': 'failed'}, status=400)
    context.update(request_data())
    context.active = context.enrich_status == ACCEPTED
    context.user = current_user
    db.session.commit()
    return jsonify({'status': 'ok'})
