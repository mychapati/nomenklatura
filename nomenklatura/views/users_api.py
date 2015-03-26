from flask import Blueprint, request
from flask.ext.login import login_user, current_user
from apikit import obj_or_404, request_data, jsonify

from nomenklatura.model import User
from nomenklatura.core import db
from nomenklatura import authz


blueprint = Blueprint('users', __name__)


@blueprint.route('/users', methods=['GET'])
def index():
    authz.require(authz.logged_in())
    users = []
    for user in User.all():
        data = user.to_dict()
        del data['email']
        users.append(data)
    return jsonify({'results': users, 'total': len(users)})


@blueprint.route('/users/<id>', methods=['GET'])
def view(id):
    user = obj_or_404(User.by_id(id))
    data = user.to_dict()
    if user.id != current_user.id:
        del data['email']
    return jsonify(data)


@blueprint.route('/users/<id>', methods=['POST', 'PUT'])
def update(id):
    user = obj_or_404(User.by_id(id))
    authz.require(user.id == current_user.id)
    user.update(request_data())
    # db.session.add(user)
    db.session.commit()
    return jsonify(user)


@blueprint.route('/users/login', methods=['POST', 'PUT'])
def login():
    user = User.by_email(request.args.get('email'))
    if user is not None and user.password == request.args.get('password'):
        login_user(user, remember=True)
        return jsonify({'status': 'ok', 'user': user})
    message = {'password': 'Invalid email or password.'}
    return jsonify({'status': 'error', 'errors': message}, status=400)


@blueprint.route('/users/register', methods=['POST', 'PUT'])
def register():
    user = User.create(request_data())
    db.session.commit()
    login_user(user, remember=True)
    return jsonify(user)


@blueprint.route('/users/reset', methods=['POST', 'PUT'])
def reset_password(id):
    return jsonify({})


@blueprint.route('/users/validate', methods=['GET'])
def validate_account(id):
    return jsonify({})
