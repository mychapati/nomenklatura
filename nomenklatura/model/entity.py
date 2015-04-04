from nomenklatura.core import db, url_for
from nomenklatura.schema import types, qualified, Attribute
from nomenklatura.model.common import make_key, is_list
from nomenklatura.model.statement import Statement


class Entity(object):
    """ An entity is a subject for any data collected in the system.
    It can represent a person, company or any other type of object,
    within a context. Entities never span across different contexts.
    All data associated to an entity is stored as statements, which
    all have the entity's ID as their subject. """

    def __init__(self, id=None, statements=None, assume_contexts=None):
        self.id = id or make_key()
        self.statements = statements or []
        self.assume_contexts = assume_contexts or []

    @property
    def attributes(self):
        attrs = set()
        for stmt in self.statements:
            if stmt.active and stmt.attribute in qualified:
                attrs.add(qualified[stmt.attribute])
        return attrs

    def has(self, attribute):
        return attribute in self.attributes

    def exists(self, attribute, value, context):
        for stmt in self.statements:
            if stmt.attribute == attribute and \
                    stmt.value == value and \
                    stmt.context_id == context.id:
                return True
        return False

    def set(self, attribute, value, context):
        if not isinstance(attribute, Attribute):
            attribute = self.type.attributes.get(attribute)
        if attribute is None:
            return
        values = value if is_list(value) else [value]
        for value in values:
            if not self.exists(attribute.qname, value, context):
                stmt = Statement(self.id, attribute.qname, value, context,
                                 assume_contexts=self.assume_contexts)
                db.session.add(stmt)
                self.statements.append(stmt)

    def match(self, attribute):
        if not isinstance(attribute, Attribute):
            attribute = self.type.attributes.get(attribute)
        if attribute is None:
            return
        for stmt in self.statements:
            if stmt.attribute != attribute.qname:
                continue
            if not stmt.active:
                continue
            yield stmt

    def get(self, attribute):
        if not isinstance(attribute, Attribute):
            attribute = self.type.attributes.get(attribute)
        if attribute is None:
            return
        values = []
        for stmt in self.match(attribute):
            values.append(stmt.value)
        if not attribute.many:
            return max(values) if len(values) else None
        return values

    @property
    def type(self):
        return self.get(types.Object.attributes.type) or types.Object

    @type.setter
    def type(self, type):
        self.set(types.Object.attributes.type, type)

    @property
    def label(self):
        return self.get(types.Node.attributes.label)

    @label.setter
    def label(self, label):
        self.set(types.Node.attributes.label, label)

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
