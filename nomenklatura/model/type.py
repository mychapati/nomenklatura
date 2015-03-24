from nomenklatura.model.common import NamedMixIn


class Type(NamedMixIn):
    """ A type defines a node in the graph to be a member of a
    particular class of thing, e.g. a company or a person. """

    def __init__(self, name, data):
        self.name = name
        self.label = data.get('label')
        self.abstract = data.get('abstract', False)
        self.parent = data.get('parent')

    @property
    def root(self):
        return self.parent is None

    @property
    def attributes(self):
        from nomenklatura.model.schema import attributes, types
        attrs = [] if self.root else types[self.parent].attributes
        attrs.extend([a for a in attributes if self.name in a._types])
        return attrs

    def to_dict(self):
        data = {
            'name': self.name,
            'label': self.label,
            'parent': self.parent,
            'abstract': self.abstract,
            'attributes': self.attributes
        }
        return data

    def to_index_dict(self):
        return self.name

    def to_freebase_type(self):
        return {
            'id': '/types/%s' % self.name,
            'name': self.label
        }

    def __repr__(self):
        return '<Type(%r,%r)>' % (self.name, self.label)

    def __unicode__(self):
        return self.label
