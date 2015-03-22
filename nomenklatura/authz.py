from flask import request
from flask.ext.login import current_user
from werkzeug.exceptions import Forbidden
from sqlalchemy import or_

from nomenklatura.model import Dataset


def datasets(action):
    if action == 'read' and request.authz_datasets.get('read') is None:
        q = Dataset.find_slugs()
        request.authz_datasets['read'] = [d.slug for d in q.all()]
    if action == 'edit' and request.authz_datasets.get('edit') is None:
        if current_user.is_authenticated():
            q = Dataset.find_slugs()
            q = q.filter(or_(
                Dataset.owner_id == current_user.id,
                Dataset.public == True # noqa
            ))
            request.authz_datasets['edit'] = [d.slug for d in q.all()]
        else:
            request.authz_datasets['edit'] = []
    if action == 'manage' and request.authz_datasets.get('manage') is None:
        if current_user.is_authenticated():
            q = Dataset.find_slugs()
            q = q.filter(Dataset.owner_id == current_user.id)
            request.authz_datasets['manage'] = [d.slug for d in q.all()]
        else:
            request.authz_datasets['manage'] = []
    return request.authz_datasets[action] or []


def logged_in():
    return current_user.is_authenticated()


def dataset_create():
    return logged_in()


def dataset_read(name):
    return name in datasets('read')


def dataset_edit(name):
    return name in datasets('edit')


def dataset_manage(name):
    return name in datasets('manage')


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")
