import os

from flask import render_template, request
from formencode import Invalid
from apikit import jsonify

from nomenklatura.core import app, login_manager
from nomenklatura.model import User
from nomenklatura.views.upload import section as upload
from nomenklatura.views.sessions_api import blueprint as sessions_api
from nomenklatura.views.datasets import section as datasets
from nomenklatura.views.entities import section as entities
from nomenklatura.views.reconcile import section as reconcile
from nomenklatura.views.matching import section as matching


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization') \
        or request.args.get('api_key')
    if api_key is not None:
        return User.by_api_key(api_key)


@app.before_request
def before():
    request.authz_datasets = {}


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(500)
def handle_exceptions(exc):
    message = exc.get_description(request.environ)
    message = message.replace('<p>', '').replace('</p>', '')
    body = {
        'status': exc.code,
        'name': exc.name,
        'message': message
    }
    headers = exc.get_headers(request.environ)
    return jsonify(body, status=exc.code,
                   headers=headers)


@app.errorhandler(Invalid)
def handle_invalid(exc):
    body = {
        'status': 400,
        'name': 'Invalid Data',
        'description': unicode(exc),
        'errors': exc.unpack_errors()
    }
    return jsonify(body, status=400)


app.register_blueprint(upload, url_prefix='/api/2')
app.register_blueprint(reconcile, url_prefix='/api/2')
app.register_blueprint(sessions_api, url_prefix='/api/2')
app.register_blueprint(datasets, url_prefix='/api/2')
app.register_blueprint(entities, url_prefix='/api/2')
app.register_blueprint(matching, url_prefix='/api/2')


def angular_templates():
    if app.config.get('ASSETS_DEBUG'):
        return
    partials_dir = os.path.join(app.static_folder, 'templates')
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as fh:
                yield ('/static/templates/%s' % file_path[len(partials_dir)+1:],
                       fh.read().decode('utf-8'))


@app.route('/entities')
@app.route('/entities/<path:id>')
@app.route('/datasets')
@app.route('/datasets/<path:id>')
@app.route('/profile')
@app.route('/docs/<path:id>')
@app.route('/')
def index(**kw):
    return render_template('app.html', angular_templates=angular_templates())
