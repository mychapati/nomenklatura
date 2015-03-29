from flask.ext.login import current_user
from werkzeug.exceptions import Forbidden

from nomenklatura.core import app
from nomenklatura.model.constants import READ, EDIT, MANAGE


def logged_in():
    return current_user.is_authenticated()


def role():
    if logged_in():
        return current_user.system_role
    return app.config.get('DEFAULT_ANON_ROLE')


def system_manage():
    return role() == MANAGE


def system_edit():
    return system_manage() or role() == EDIT


def system_read():
    return system_edit() or role() == READ


def require(pred):
    if not pred:
        raise Forbidden("Sorry, you're not permitted to do this!")
