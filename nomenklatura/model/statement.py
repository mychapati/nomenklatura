from normality import normalize
from sqlalchemy.ext.hybrid import hybrid_property

from nomenklatura.core import db
from nomenklatura.schema import qualified
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH


class Statement(db.Model, CommonMixIn):
    """ Statements are facts that relate to an entity. Each statement
    has a subject (the entity), an attribute (a predefined, typed
    property name) and an object (the value of the statement). """

    __tablename__ = 'statement'

    subject = db.Column(db.String(KEY_LENGTH), index=True)
    attribute = db.Column(db.String(1024), index=True)
    _value = db.Column('value', db.Unicode, index=True)
    normalized = db.deferred(db.Column(db.Unicode))
    inferred_via = db.Column(db.String(KEY_LENGTH * 4))
    deleted_at = db.Column(db.DateTime, nullable=True)

    context_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('context.id'))
    context = db.relationship('Context', backref=db.backref('statements',
                         lazy='dynamic', cascade='all, delete-orphan')) # noqa

    def __init__(self, subject, attribute, value, context,
                 assume_contexts=None):
        self.subject = subject
        self.attribute = attribute
        self.value = value
        self.context = context
        self.assume_contexts = assume_contexts or []

    @hybrid_property
    def value(self):
        attr = qualified[self.attribute]
        conv = attr.converter(attr)
        return conv.deserialize_safe(self._value)

    @value.setter
    def value(self, value):
        attr = qualified[self.attribute]
        conv = attr.converter(attr)
        self._value = conv.serialize_safe(value)
        self.normalized = normalize(self._value)

    @property
    def active(self):
        if self.deleted_at:
            return False
        if hasattr(self, 'assume_contexts') and \
                self.context_id in self.assume_contexts:
            return True
        if self.context is None:
            return False
        return self.context.active

    def to_dict(self, raw=False):
        return {
            'id': self.id,
            'subject': self.subject,
            'attribute': self.attribute,
            'value': self._value if raw else self.value,
            'inferred_via': self.inferred_via,
            'context_id': self.context_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def __cmp__(self, other):
        if other is None:
            return 1
        return cmp(self.updated_at, other.updated_at)

    def __repr__(self):
        return u'<Statement(%s,%s,%r)>' % (self.subject, self.attribute,
                                           self.value)
