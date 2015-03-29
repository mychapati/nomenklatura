from flask import request
from colander import Invalid
from apikit import jsonify

from nomenklatura.core import login_manager, app_name, app_title
from nomenklatura.schema import DataException
from nomenklatura.model import User
from nomenklatura.views.ui import app
from nomenklatura.views.users_api import blueprint as users_api
from nomenklatura.views.imports_api import blueprint as imports_api
from nomenklatura.views.core_api import blueprint as core_api
from nomenklatura.views.entities_api import blueprint as entities_api
from nomenklatura.views.contexts_api import blueprint as contexts_api
from nomenklatura.views.pairings_api import blueprint as pairings_api
from nomenklatura.views.reconcile_api import blueprint as reconcile_api


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization') \
        or request.args.get('api_key')
    if api_key is not None:
        return User.by_api_key(api_key)


@app.context_processor
def template_context_processor():
    return {
        'APP_NAME': app_name,
        'APP_TITLE': app_title
    }


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
        'errors': exc.asdict()
    }
    return jsonify(body, status=400)


@app.errorhandler(DataException)
def handle_data_exception(exc):
    body = {
        'status': 400,
        'name': exc.message,
        'errors': {
            exc.attribute.name: exc.message
        },
        'data_type': unicode(exc.data_type),
        'value': exc.value
    }
    return jsonify(body, status=400)


app.register_blueprint(users_api, url_prefix='/api/2')
app.register_blueprint(core_api, url_prefix='/api/2')
app.register_blueprint(entities_api, url_prefix='/api/2')
app.register_blueprint(contexts_api, url_prefix='/api/2')
app.register_blueprint(pairings_api, url_prefix='/api/2')
app.register_blueprint(reconcile_api, url_prefix='/api/2')
app.register_blueprint(imports_api, url_prefix='/api/2')
