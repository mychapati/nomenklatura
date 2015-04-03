import os

import yaml

from nomenklatura.schema.attribute import Attribute
from nomenklatura.schema.type import Type
from nomenklatura.schema.schema import Schema
from nomenklatura.schema.data_types import DataException # noqa


DEFAULT_SCHEMA = os.path.join(os.path.dirname(__file__), 'schema.yaml')


def load_schema():
    """ Load types and attributes from a ``.yaml`` file specified. """

    types, attributes = Schema(Type), Schema(Attribute)

    with open(DEFAULT_SCHEMA, 'rb') as fh:
        data = yaml.load(fh)

        for name, obj in data.get('types', {}).items():
            types._items[name] = Type(name, obj)

        for name, obj in data.get('attributes', {}).items():
            attributes._items[name] = Attribute(name, obj)

    return types, attributes

types, attributes = load_schema()
