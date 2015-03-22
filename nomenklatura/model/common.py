import re
import string
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, DateTime


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


class NKException(Exception):
    pass


class CommonMixIn(object):
    id = Column(String(KEY_LENGTH), primary_key=True, default=make_key)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class NamedMixIn(object):

    def __eq__(self, other):
        if self.name == other:
            return True
        if hasattr(other, 'name') and self.name == other.name:
            return True
        return False
