from flask import Blueprint, request, redirect
from flask.ext.login import login_user, current_user
from apikit import obj_or_404, request_data, jsonify

from nomenklatura.model import User
from nomenklatura.core import db, app
from nomenklatura.notification import send_activation_link, send_reset_link
from nomenklatura.views import authz


blueprint = Blueprint('users', __name__)


@blueprint.route('/users', methods=['GET'])
def index():
    authz.require(authz.system_manage())
    users = list(User.all())
    return jsonify({'results': users, 'total': len(users)})


@blueprint.route('/users/<id>', methods=['GET'])
def view(id):
    authz.require(authz.system_read())
    user = obj_or_404(User.by_id(id))
    data = user.to_dict()
    return jsonify(data)


@blueprint.route('/users/<id>', methods=['POST', 'PUT'])
def update(id):
    user = obj_or_404(User.by_id(id))
    authz.require(user.id == current_user.id or authz.system_manage())
    user.update(request_data())
    db.session.commit()
    return jsonify(user)


@blueprint.route('/users/login', methods=['POST', 'PUT'])
def login():
    data = request_data()
    user = User.by_email(data.get('email'))
    if user is not None and user.verify(data.get('password')):
        login_user(user, remember=True)
        return jsonify({'status': 200, 'user': user})
    message = {'password': 'Invalid email or password.'}
    return jsonify({'status': 400, 'errors': message}, status=400)


@blueprint.route('/users/register', methods=['POST', 'PUT'])
def register():
    user = User.create(request_data())
    db.session.commit()
    send_activation_link(user)
    return jsonify(user)


@blueprint.route('/users/reset', methods=['POST', 'PUT'])
def reset_password():
    user = User.by_email(request_data().get('email'))
    if user is None:
        message = {'email': 'This email address is not linked to a user.'}
        return jsonify({'status': 400, 'errors': message}, status=400)
    send_reset_link(user)
    return jsonify({'status': 200})


@app.route('/validate/<id>', methods=['GET'])
def validate_account(id):
    user = User.by_id(id)
    if user is not None and user.validation_token == request.args.get('token'):
        user.validated = True
        db.session.commit()
        login_user(user, remember=True)
    return redirect('/')
