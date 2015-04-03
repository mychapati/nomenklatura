import dateutil.parser


def date_parse(text):
    try:
        return dateutil.parser.parse(text)
    except (TypeError, ValueError):
        return None


class NamedMixIn(object):

    def __eq__(self, other):
        if self.name == other:
            return True
        if hasattr(other, 'name') and self.name == other.name:
            return True
        return False
