import dateutil.parser
from normality import normalize


def date_parse(text):
    try:
        return dateutil.parser.parse(text)
    except (TypeError, ValueError, AttributeError):
        return None


def is_list(obj):
    return isinstance(obj, (list, tuple, set))


class SchemaObject(object):

    def __init__(self, name, label, abstract=False):
        self.name = name
        self.label = label
        self.abstract = abstract

    def __eq__(self, other):
        if self.name == other:
            return True
        if hasattr(other, 'name') and self.name == other.name:
            return True
        return False

    def match_prefix(self, prefix):
        prefix = normalize(prefix)
        if not self.abstract:
            if normalize(self.name).startswith(prefix):
                return True
            elif normalize(self.label).startswith(prefix):
                return True
        return False
