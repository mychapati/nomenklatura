from flask import session, Blueprint, redirect, request
from flask.ext.login import login_user, logout_user, current_user
from werkzeug.exceptions import BadRequest
from apikit import jsonify

from nomenklatura import authz
from nomenklatura.core import db, url_for
from nomenklatura.model import User


blueprint = Blueprint('sessions', __name__)


@blueprint.route('/sessions')
def status():
    permissions = {}
    for perm in ['read', 'edit', 'manage']:
        permissions[perm] = authz.datasets(perm)

    return jsonify({
        'logged_in': authz.logged_in(),
        'api_key': current_user.api_key if authz.logged_in() else None,
        'user': current_user if authz.logged_in() else None,
        'permissions': permissions,
        'logout': url_for('.logout')
    })


@blueprint.route('/sessions/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next_url', url_for('index')))
