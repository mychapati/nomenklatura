import logging
from flask_mail import Message

from nomenklatura.core import app, mail, url_for

log = logging.getLogger(__name__)


RESET_MESSAGE = """
Someone (possibly you) has requested a password reset for your
user account. If you want to set a new password, please click
the link below to be logged in automatically, then set a new
password.

%s

"""

ACTIVATION_MESSAGE = """
Thank you for signing up! Please confirm your email address by
clicking the link below:

%s

"""


def send_reset_link(user):
    send_validation_link(user, 'Reset your password', RESET_MESSAGE)


def send_activation_link(user):
    send_validation_link(user, 'Activate your account', ACTIVATION_MESSAGE)


def send_validation_link(user, subject, message):
    url = url_for('validate_account', id=user.id,
                  token=user.validation_token)
    log.debug('Activation URL: %s', url)
    try:
        msg = Message(subject, recipients=[user.email])
        msg.body = message % url
        mail.send(msg)
    except Exception, e:
        log.exception(e)
