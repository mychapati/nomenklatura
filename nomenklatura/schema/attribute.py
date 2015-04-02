from nomenklatura.schema.data_types import DATA_TYPES
from nomenklatura.schema.common import NamedMixIn


class Attribute(NamedMixIn):
    """ An attribute is a named property that a node in the graph
    may have assinged to it. """

    def __init__(self, name, data):
        self.name = name
        self.abstract = False
        self.label = data.get('label')
        self.data_type = data.get('data_type')
        self._types = data.get('types', ['Object'])
        self.many = data.get('many', False)

    @property
    def types(self):
        from nomenklatura.schema import types
        types_ = []
        for t in types:
            for a in t.attributes:
                if a == self:
                    types_.append(t)
        return types_

    @property
    def converter(self):
        """ Instantiate a type converter for this attribute. """
        if self.data_type not in DATA_TYPES:
            raise TypeError('Invalid data type: %s'
                            % self.data_type)
        return DATA_TYPES[self.data_type]

    def to_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'many': self.many,
            'data_type': self.data_type
        }

    def to_index_dict(self):
        return self.name

    def __repr__(self):
        return '<Attribute(%r,%r)>' % (self.name, self.data_type)

    def __eq__(self, other):
        if hasattr(other, 'name'):
            return self.name == other.name
        return self.name == other

    def __unicode__(self):
        return self.name
