import os
import yaml

from nomenklatura.schema.type import Type
from nomenklatura.schema.schema import Schema
from nomenklatura.schema.data_types import DataException # noqa


DEFAULT_SCHEMA = os.path.join(os.path.dirname(__file__), 'schema.yaml')


def qualified():
    attributes = {}
    for type_ in types:
        for attr in type_.attributes:
            attributes[attr.qname] = attr
    return attributes


def load_schema():
    """ Load types and attributes from a ``.yaml`` file specified. """
    types = Schema(Type)
    with open(DEFAULT_SCHEMA, 'rb') as fh:
        data = yaml.load(fh)
        for name, obj in data.get('types', {}).items():
            types._items[name] = Type(name, obj)
    return types


types = load_schema()
