import dateutil.parser

from nomenklatura.model.common import NKException


class DataType(object):

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value

    def serialize_safe(self, value):
        if value is None:
            return None
        return self.serialize(value)

    def deserialize_safe(self, value):
        if value is None:
            return None
        try:
            return self.deserialize(value)
        except Exception, e:
            if isinstance(e, NKException):
                raise
            raise NKException(unicode(e))


class String(DataType):
    pass


class Integer(DataType):

    def serialize(self, value):
        return unicode(value)

    def deserialize(self, value):
        return int(value)


class Float(DataType):

    def serialize(self, value):
        return unicode(value)

    def deserialize(self, value):
        return float(value)


class DateTime(DataType):

    def serialize(self, value):
        return value.isoformat()

    def deserialize(self, value):
        return dateutil.parser.parse(value)


class Type(DataType):

    def serialize(self, value):
        if hasattr(value, 'name'):
            return value.name
        return value

    def deserialize(self, value):
        from nomenklatura.model.schema import types
        type = types[value]
        if type is None:
            raise NKException("Unknown entity type: %s" % value)
        return type


class Entity(DataType):

    def serialize(self, entity):
        return entity.id

    def deserialize(self, value):
        # from nomenklatura.model.entity import Entity
        raise NotImplemented()


DATA_TYPES = {
    'string': String,
    'text': String,
    'integer': Integer,
    'int': Integer,
    'float': Float,
    'datetime': DateTime,
    'type': Type,
    'entity': Entity
}
