import os

import yaml
from normality import normalize

from nomenklatura.model.attribute import Attribute
from nomenklatura.model.type import Type

DEFAULT_SCHEMA = os.path.join(os.path.dirname(__file__), 'schema.yaml')


class Map(object):
    """ A simple proxy object so you can request
    ``types.Company`` or ``attributes.label``. """

    def __init__(self, cls, items=None):
        self.cls = cls
        self._items = items or {}

    def __getitem__(self, name):
        return self._items.get(name)

    def get(self, name):
        if isinstance(name, self.cls):
            return name
        return self[name]

    def suggest(self, prefix):
        prefix = normalize(prefix)
        for cand in self:
            if normalize(cand.name).startswith(prefix):
                yield cand
            elif normalize(cand.label).startswith(prefix):
                yield cand

    def __iter__(self):
        return iter(self._items.values())

    def __contains__(self, name):
        return name in self._items

    def __getattr__(self, name):
        return self.__getitem__(name)


def load_schema():
    """ Load types and attributes from a ``.yaml`` file specified into
    the given dataset. """

    types, attributes = Map(Type), Map(Attribute)

    with open(DEFAULT_SCHEMA, 'rb') as fh:
        data = yaml.load(fh)

        for name, obj in data.get('types', {}).items():
            types._items[name] = Type(name, obj)

        for name, obj in data.get('attributes', {}).items():
            attributes._items[name] = Attribute(name, obj)

    return types, attributes

types, attributes = load_schema()
