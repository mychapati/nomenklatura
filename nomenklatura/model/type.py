from nomenklatura.model.common import NamedMixIn


class Type(NamedMixIn):
    """ A type defines a node in the graph to be a member of a
    particular class of thing, e.g. a company or a person. """

    def __init__(self, name, data):
        self.name = name
        self.label = data.get('label')

    def to_dict(self):
        return {
            'name': self.name,
            'label': self.label
        }

    def __repr__(self):
        return '<Type(%r,%r)>' % (self.name, self.label)

    def __unicode__(self):
        return self.label
