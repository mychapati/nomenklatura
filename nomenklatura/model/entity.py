from nomenklatura.core import db, url_for
from nomenklatura.schema import types
from nomenklatura.model.common import make_key, is_list
from nomenklatura.model.statement import Statement

base_attributes = types.Object.attributes


class Entity(object):
    """ An entity is a subject for any data collected in the system.
    It can represent a person, company or any other type of object,
    within a context. Entities never span across different contexts.
    All data associated to an entity is stored as statements, which
    all have the entity's ID as their subject. """

    def __init__(self, id=None, statements=None):
        self.id = id or make_key()
        self.statements = statements or []

    @property
    def attributes(self):
        attrs = set()
        for stmt in self.statements:
            if stmt.active:
                attrs.add(stmt.attribute)
        return attrs

    def has(self, attribute):
        return attribute in self.attributes

    def set(self, attribute, value, context):
        attribute = self.type.attributes.get(attribute)
        values = value if is_list(value) else [value]
        for value in values:
            stmt = Statement(self.id, attribute.qname,
                             value, context)
            db.session.add(stmt)
            self.statements.append(stmt)

    def match(self, attribute):
        attribute = self.type.attributes.get(attribute)
        for stmt in self.statements:
            if stmt.attribute != attribute.qname:
                continue
            if not stmt.active:
                continue
            yield stmt

    def get(self, attribute):
        attribute = self.type.attributes.get(attribute)
        values = []
        for stmt in self.match(attribute):
            values.append(stmt.value)
        if not attribute.many:
            return max(values) if len(values) else None
        return values

    @property
    def type(self):
        return self.get(base_attributes.type) or types.Object

    @type.setter
    def type(self, type):
        self.set(base_attributes.type, type)

    @property
    def label(self):
        return self.get(base_attributes.type.label)

    @label.setter
    def label(self, label):
        self.set(base_attributes.type.label, label)

    def to_dict(self):
        data = self.to_index_dict()
        for attribute in self.attributes:
            vals = self.get(attribute)
            vals = vals if attribute.many else [vals]
            data[attribute.name] = []
            for val in vals:
                if hasattr(val, 'to_index_dict'):
                    val = val.to_index_dict()
                data[attribute.name].append(val)
            if not attribute.many:
                data[attribute.name] = data[attribute.name][0]
        return data

    def to_index_dict(self):
        return {
            'id': self.id,
            'api_url': url_for('entities.view', id=self.id),
            'label': self.label,
            'type': unicode(self.type)
        }

    @classmethod
    def create(cls, data, context):
        entity = Entity()
        entity.update(data, context)
        return entity

    def update(self, data, context):
        if 'type' in data:
            self.set(types.Object.attributes.type, data.pop('type'), context)
        for attribute in self.type.attributes:
            if attribute.name in data:
                self.set(attribute, data.get(attribute.name), context)

    def __repr__(self):
        return u'<Entity(%r, %s, %r)>' % (self.id, self.type, self.label)

    def __len__(self):
        return len(self.statements)

    def __iter__(self):
        return iter(self.statements)

    def __unicode__(self):
        return self.id
