from flask.ext.login import current_user
from werkzeug.exceptions import Forbidden


def logged_in():
    return current_user.is_authenticated()


def dataset_create():
    return logged_in()


def dataset_edit(dataset):
    if not logged_in():
        return False
    if dataset.public_edit:
        return True
    if dataset.owner_id == current_user.id:
        return True
    return False


def dataset_manage(dataset):
    if not logged_in():
        return False
    if dataset.owner_id == current_user.id:
        return True
    return False


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")
