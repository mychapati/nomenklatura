
class NamedMixIn(object):

    def __eq__(self, other):
        if self.name == other:
            return True
        if hasattr(other, 'name') and self.name == other.name:
            return True
        return False
