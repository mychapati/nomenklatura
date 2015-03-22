from nomenklatura.core import db, url_for
from nomenklatura.model.common import make_key
from nomenklatura.model.attribute import Attribute
from nomenklatura.model.schema import attributes
from nomenklatura.model.statement import Statement


class Entity(object):
    """ An entity is a subject for any data collected in the system.
    It can represent a person, company or any other type of object,
    within a context. Entities never span across different contexts.
    All data associated to an entity is stored as statements, which
    all have the entity's ID as their subject. """

    def __init__(self, dataset, id=None, statements=None):
        self.dataset = dataset
        self.id = id or make_key()
        self.statements = statements or []

    @property
    def attributes(self):
        attributes = set()
        for stmt in self.statements:
            attributes.add(stmt.attribute)
        return attributes

    def has(self, attribute):
        return attribute in self.attributes

    def set(self, attribute, value, context=None):
        if not isinstance(attribute, Attribute):
            attribute = attributes.get(attribute)
        stmt = Statement(self.dataset, self.id, attribute, value,
                         context=context)
        db.session.add(stmt)
        self.statements.append(stmt)
        return stmt

    def match(self, attribute):
        if not isinstance(attribute, Attribute):
            attribute = attributes.get(attribute)
        for stmt in self.statements:
            if stmt.attribute != attribute:
                continue
            yield stmt

    def get(self, attribute):
        for stmt in self.match(attribute):
            return stmt.value

    @property
    def type(self):
        return self.get(attributes.type)

    @type.setter
    def type(self, type):
        self.set(attributes.type, type)

    @property
    def label(self):
        return self.get(attributes.label)

    @label.setter
    def label(self, label):
        self.set(attributes.label, label)

    def to_dict(self):
        url = url_for('entities.view', dataset=self.dataset.slug, id=self.id)
        data = {
            'id': self.id,
            'api_url': url
        }
        for attribute in self.attributes:
            data[attribute.key] = self.get(attribute)
        return data

    @classmethod
    def create(cls, dataset, data, user):
        # TODO: crutch. Replace with a better thing asap.
        entity = Entity(dataset)
        entity.update(data, user)
        return entity

    def update(self, data, user):
        # TODO: crutch. Replace with a better thing asap.
        for key, value in data.items():
            attribute = attributes.get(key)
            if attribute is None:
                continue
            self.set(attribute, value)

    def __repr__(self):
        return u'<Entity(%r, %s, %r)>' % (self.id, self.type, self.label)

    def __len__(self):
        return len(self.statements)

    def __iter__(self):
        return self.statements

    def __unicode__(self):
        return self.label or self.id
