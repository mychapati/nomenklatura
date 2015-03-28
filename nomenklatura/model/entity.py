from nomenklatura.core import db, url_for
from nomenklatura.schema import attributes, types
from nomenklatura.model.common import make_key
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
        attrs = set()
        for stmt in self.statements:
            if stmt.active:
                attrs.add(stmt.attribute)
        return attrs

    def has(self, attribute):
        return attribute in self.attributes

    def set(self, attribute, value, context):
        attribute = attributes.get(attribute)
        values = value if attribute.many else [value]
        for value in values:
            stmt = Statement(self.dataset, self.id, attribute,
                             value, context)
            db.session.add(stmt)
            self.statements.append(stmt)

    def match(self, attribute):
        attribute = attributes.get(attribute)
        for stmt in self.statements:
            if stmt.attribute != attribute:
                continue
            if not stmt.active:
                continue
            yield stmt

    def get(self, attribute):
        attribute = attributes.get(attribute)
        values = []
        for stmt in self.match(attribute):
            values.append(stmt.value)
        if not attribute.many:
            return max(values) if len(values) else None
        return values

    @property
    def type(self):
        return self.get(attributes.type) or types.Thing

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
        url = url_for('entities.view', dataset=self.dataset.slug, id=self.id)
        return {
            'id': self.id,
            'api_url': url,
            'label': self.label,
            'type': unicode(self.type)
        }

    @classmethod
    def create(cls, dataset, data, context):
        # TODO: crutch. Replace with a better thing asap.
        entity = Entity(dataset)
        entity.update(data, context)
        return entity

    def update(self, data, context):
        # TODO: crutch. Replace with a better thing asap.
        for attribute in attributes:
            if attribute.name in data:
                self.set(attribute, data.get(attribute.name), context)

    def __repr__(self):
        return u'<Entity(%r, %s, %r)>' % (self.id, self.type, self.label)

    def __len__(self):
        return len(self.statements)

    def __iter__(self):
        return iter(self.statements)

    def __unicode__(self):
        return self.label or self.id
