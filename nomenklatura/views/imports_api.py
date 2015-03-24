from flask import Blueprint, request
from flask.ext.login import current_user
# from colander import Invalid
from werkzeug.exceptions import BadRequest
from apikit import jsonify, obj_or_404

from nomenklatura import authz
from nomenklatura.core import db
from nomenklatura.model import Dataset, Context
from nomenklatura.model.imports import store_upload
from nomenklatura.model.imports import analyze_upload, get_table

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
        'source': dict(source.meta),
        'table': dict(table.meta)
    })


@blueprint.route('/datasets/<dataset>/imports/<id>', methods=['POST'])
def process(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    context = obj_or_404(Context.by_id(id))
    raise NotImplemented()
    return view(dataset.slug, id)
