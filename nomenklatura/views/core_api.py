from flask import Blueprint, redirect, request
from flask.ext.login import logout_user, current_user
from apikit import jsonify

from nomenklautea.core import url_for
from nomenklatura.views import authz
from nomenklatura.schema import attributes, types
from nomenklatura.model.constants import READ, EDIT, MANAGE


blueprint = Blueprint('schema', __name__)


@blueprint.route('/schema')
def schema():
    return jsonify({
        'attributes': attributes._items,
        'types': types._items
    })


@blueprint.route('/sessions')
def status():
    return jsonify({
        'logged_in': authz.logged_in(),
        'api_key': current_user.api_key if authz.logged_in() else None,
        'user': current_user if authz.logged_in() else None,
        'permissions': {
            READ: authz.system_read(),
            EDIT: authz.system_edit(),
            MANAGE: authz.system_manage()
        },
        'logout': url_for('.logout')
    })


@blueprint.route('/sessions/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next_url', url_for('index')))
