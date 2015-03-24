from flask import Blueprint, request
from colander import Invalid
from apikit import jsonify, request_data, obj_or_404

from nomenklatura import authz
from nomenklatura.core import db
from nomenklatura.model import Dataset

blueprint = Blueprint('upload', __name__)


@blueprint.route('/datasets/<dataset>/uploads', methods=['POST'])
def upload(dataset):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    file_ = request.files.get('file')
    if not file_ or not file_.filename:
        err = {'file': "You need to upload a file"}
        raise Invalid("No file.", None, None, error_dict=err)
    upload = Upload.create(dataset, request.user, file_)
    db.session.commit()
    return jsonify(upload)


@blueprint.route('/datasets/<dataset>/uploads/<id>', methods=['GET'])
def view(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    upload = obj_or_404(Upload.by_id(dataset, id))
    return jsonify(upload)


@blueprint.route('/datasets/<dataset>/uploads/<id>', methods=['POST'])
def process(dataset, id):
    authz.require(authz.dataset_edit(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))

    upload = obj_or_404(Upload.by_id(dataset, id))
    mapping = request_data()
    mapping['reviewed'] = mapping.get('reviewed') or False
    mapping['columns'] = mapping.get('columns', {})
    fields = mapping['columns'].values()
    for header in mapping['columns'].keys():
        if header not in upload.tab.headers:
            raise Invalid("Invalid header: %s" % header, None, None)

    if 'name' not in fields and 'id' not in fields:
        raise Invalid("You have not selected a field that definies entity names.", None, None)

    import_upload.delay(upload.id, request.user.id, mapping)
    return jsonify({'status': 'Loading data...'})
