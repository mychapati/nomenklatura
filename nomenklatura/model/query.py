

class EntityQuery(object):

    def __init__(self, dataset=None, limit=None, offset=None):
        self._dataset = dataset
        self._limit = limit
        self._offset = offset

    def clone(self):
        return EntityQuery(dataset=self._dataset, limit=self._limit,
                           offset=self._offset)

    def filter_dataset(self, dataset):
        q = self.clone()
        q._dataset = dataset
        return q

    def limit(self, n):
        q = self.clone()
        q._limit = n
        return q

    def offset(self, n):
        q = self.clone()
        q._offset = n
        return q

    def count(self):
        return 0

    def __len__(self):
        return self.count()

    def __iter__(self):
        return iter([])
