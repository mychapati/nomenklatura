import string
from uuid import uuid4
from datetime import datetime

from nomenklatura.core import db


ALPHABET = string.ascii_lowercase + string.digits


def make_key():
    num = uuid4().int
    s = []
    while True:
        num, r = divmod(num, len(ALPHABET))
        s.append(ALPHABET[r])
        if num == 0:
            break
    return ''.join(reversed(s))

KEY_LENGTH = len(make_key())


class CommonMixIn(object):
    id = db.Column(db.String(KEY_LENGTH), primary_key=True, default=make_key)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
