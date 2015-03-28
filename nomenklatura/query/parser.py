from nomenklatura.schema import attributes


class QueryNode(object):

    def __init__(self, parent, name, data):
        self.parent = parent
        self.name = name
        self.raw = data

        self.many = False
        if isinstance(data, (list, tuple, set)):
            self.many = True
            if not len(data):
                data = None
            data = data[0]

        if data is not None and isinstance(data, dict):
            self.limit = data.pop('limit', 15)
            if not self.many:
                self.limit = 1
            self.offset = data.pop('offset', 0)

        self.data = data
        self.attribute = attributes[self.name]

    @property
    def attributes(self):
        if self.name == '*':
            return set(attributes)
        if self.attribute is not None:
            return set([self.attribute])

    @property
    def root(self):
        return self.parent is None

    @property
    def blank(self):
        return self.data is None

    @property
    def value(self):
        return self.data

    @property
    def leaf(self):
        return not isinstance(self.data, dict)

    @property
    def filtered(self):
        if self.leaf:
            return self.data is not None
        for child in self.children:
            if child.filtered:
                return True
        return False

    @property
    def children(self):
        if self.leaf:
            return
        for name, data in self.data.items():
            yield QueryNode(self, name, data)

    def to_dict(self):
        data = {
            'name': self.name,
            'leaf': self.leaf,
            'many': self.many,
            'blank': self.blank,
            'filtered': self.filtered
        }
        if self.root:
            data['limit'] = self.limit
            data['offset'] = self.offset
        if self.leaf:
            data['value'] = self.data if self.leaf else None
        else:
            data['children'] = [c.to_dict() for c in self.children]
        return data
