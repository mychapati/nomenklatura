from flask import Blueprint, request
from flask.ext.login import current_user
# from colander import Invalid
from werkzeug.exceptions import BadRequest
from apikit import jsonify, obj_or_404, get_limit, get_offset

from nomenklatura import authz
from nomenklatura.core import db
from nomenklatura.model import Dataset, Context
from nomenklatura.model.imports import store_upload, load_upload, set_state
from nomenklatura.model.imports import analyze_upload, get_table, get_logs

blueprint = Blueprint('imports', __name__)


@blueprint.route('/datasets/<dataset>/imports', methods=['POST'])
def upload(dataset):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    file_ = request.files.get('file')
    if not file_ or not file_.filename:
        raise BadRequest("You need to upload a file")
    context = store_upload(dataset, file_, file_.filename, current_user)
    db.session.commit()
    analyze_upload.delay(context.id)
    return jsonify(context)


@blueprint.route('/datasets/<dataset>/imports/<id>', methods=['GET'])
def view(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = obj_or_404(Context.by_id(id))
    source, table = get_table(context)
    return jsonify({
        'context': context,
        'context_statements': context.statements.count(),
        'mapping': context.resource_mapping,
        'source': dict(source.meta),
        'table': dict(table.meta)
    })


@blueprint.route('/datasets/<dataset>/imports/<id>', methods=['POST'])
def load(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = obj_or_404(Context.by_id(id))
    source, table = get_table(context)
    set_state(source, 'loading')
    load_upload.delay(context.id)
    return jsonify({'status': 'ok'})


@blueprint.route('/datasets/<dataset>/imports/<id>/logs', methods=['GET'])
def logs(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = obj_or_404(Context.by_id(id))
    logs = get_logs(context, get_limit(default=10), get_offset())
    return jsonify({'entries': list(logs)})
