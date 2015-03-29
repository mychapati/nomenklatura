from flask import Blueprint, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404, arg_bool

from nomenklatura.core import db, url_for
from nomenklatura.views import authz
from nomenklatura.model import Context
from nomenklatura.processing import process_updates

blueprint = Blueprint('contexts', __name__)


@blueprint.route('/contexts', methods=['GET'])
def index():
    authz.require(authz.system_read())
    q = Context.all()
    if arg_bool('imports'):
        q = q.filter(Context.resource_name != None) # noqa
    q = q.order_by(Context.updated_at.desc())
    return jsonify(Pager(q))


@blueprint.route('/contexts', methods=['POST'])
def create():
    authz.require(authz.system_edit())
    context = Context.create(current_user, request_data())
    db.session.commit()
    return redirect(url_for('.view', id=context.id))


@blueprint.route('/contexts/<id>', methods=['GET'])
def view(id):
    authz.require(authz.system_read())
    context = obj_or_404(Context.by_id(id))
    return jsonify(context)


@blueprint.route('/contexts/<id>', methods=['POST'])
def update(id):
    authz.require(authz.system_edit())
    context = obj_or_404(Context.by_id(id))
    context.update(request_data())
    db.session.commit()
    process_updates.delay()
    return redirect(url_for('.view', id=context.id))
