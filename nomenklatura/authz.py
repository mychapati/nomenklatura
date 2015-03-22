from flask import request
from flask.ext.login import current_user
from werkzeug.exceptions import Forbidden

from nomenklatura.core import db
from nomenklatura.model import Dataset, Role


def datasets(action):
    if 'read' not in request.authz_datasets:
        request.authz_datasets['read'] = []
        request.authz_datasets['edit'] = []
        request.authz_datasets['manage'] = []

        q = db.session.query(Dataset.slug)
        q = q.filter(Dataset.public == True) # noqa
        request.authz_datasets['read'] = [r.slug for r in q]

        if current_user.is_authenticated():
            q = db.session.query(Dataset.slug, Role.role)
            q = q.join(Role)
            q = q.filter(Role.user_id == current_user.id)

            for row in q:
                if row.slug not in request.authz_datasets['read']:
                    request.authz_datasets['read'].append(row.slug)
                if row.role == Role.EDIT or row.role == Role.MANAGE:
                    request.authz_datasets['edit'].append(row.slug)
                if row.role == Role.MANAGE:
                    request.authz_datasets['manage'].append(row.slug)

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
