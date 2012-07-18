from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect
from formencode import Invalid, htmlfill

from linkspotting.core import db
from linkspotting.util import request_content, response_format
from linkspotting.util import jsonify, Pager
from linkspotting import authz
from linkspotting.views.common import handle_invalid
from linkspotting.model import Dataset, Link, Value
from linkspotting.matching import get_algorithms

section = Blueprint('dataset', __name__)

@section.route('/new', methods=['GET'])
def new():
    authz.require(authz.dataset_create())
    return render_template('dataset/new.html')

@section.route('/datasets', methods=['GET'])
def index():
    format = response_format()
    if format == 'json':
        return jsonify(Dataset.all())
    return "Not implemented!"

@section.route('/', methods=['POST'])
def create():
    authz.require(authz.dataset_create())
    data = request_content()
    try:
        dataset = Dataset.create(data, request.account)
        db.session.commit()
        return redirect(url_for('.view', dataset=dataset.name))
    except Invalid, inv:
        return handle_invalid(inv, new, data=data)

@section.route('/<dataset>', methods=['GET'])
def view(dataset):
    dataset = Dataset.find(dataset)
    format = response_format()
    if format == 'json':
        return jsonify(dataset)
    unmatched = Link.all_unmatched(dataset).count()
    values = Value.all(dataset,
            query=request.args.get('query'))
    pager = Pager(values, '.view', dataset=dataset.name,
                  limit=10)
    return render_template('dataset/view.html',
            values=pager,
            query=request.args.get('query', ''),
            dataset=dataset, unmatched=unmatched)

@section.route('/<dataset>/edit', methods=['GET'])
def edit(dataset):
    dataset = Dataset.find(dataset)
    authz.require(authz.dataset_manage(dataset))
    html = render_template('dataset/edit.html',
                           dataset=dataset,
                           algorithms=get_algorithms())
    return htmlfill.render(html, defaults=dataset.as_dict())

@section.route('/<dataset>', methods=['POST'])
def update(dataset):
    dataset = Dataset.find(dataset)
    authz.require(authz.dataset_manage(dataset))
    data = request_content()
    try:
        dataset.update(data)
        db.session.commit()
        flash("Updated %s" % dataset.label, 'success')
        return redirect(url_for('.view', dataset=dataset.name))
    except Invalid, inv:
        return handle_invalid(inv, edit, 
                args=[dataset.name], data=data)


