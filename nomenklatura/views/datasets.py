from flask import Blueprint, url_for, redirect
from flask.ext.login import current_user
from apikit import jsonify, Pager, request_data, obj_or_404

from nomenklatura.core import db
from nomenklatura import authz
from nomenklatura.model import Dataset
from nomenklatura.model.matching import attribute_keys

section = Blueprint('datasets', __name__)


@section.route('/datasets', methods=['GET'])
def index():
    q = Dataset.all()
    q = q.filter(Dataset.slug.in_(authz.datasets('read')))
    pager = Pager(q)
    return jsonify(pager.to_dict())


@section.route('/datasets', methods=['POST'])
def create():
    authz.require(authz.dataset_create())
    dataset = Dataset.create(request_data(), current_user)
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.name))


@section.route('/datasets/<dataset>', methods=['GET'])
def view(dataset):
    dataset = obj_or_404(Dataset.by_slug(dataset))
    return jsonify(dataset)


@section.route('/datasets/<dataset>/attributes', methods=['GET'])
def attributes(dataset):
    dataset = obj_or_404(Dataset.by_slug(dataset))
    return jsonify({'attributes': attribute_keys(dataset)})


@section.route('/datasets/<dataset>', methods=['POST'])
def update(dataset):
    authz.require(authz.dataset_manage(dataset))
    dataset = obj_or_404(Dataset.by_slug(dataset))
    dataset.update(request_data())
    db.session.commit()
    return redirect(url_for('.view', dataset=dataset.name))
