from sqlalchemy.orm import aliased

from nomenklatura.core import db, url_for
from nomenklatura.schema import attributes
from nomenklatura.model.statement import Statement
from nomenklatura.model.context import Context
# from nomenklatura.model.type import Type


class QueryBuilder(object):

    def __init__(self, dataset, parent, node):
        self.dataset = dataset
        self.parent = parent
        self.node = node
        self.results = {}

    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = []
            for child_node in self.node.children:
                qb = QueryBuilder(self.dataset, self, child_node)
                self._children.append(qb)
        return self._children

    def _add_statement(self, q):
        """ Generate a linked statement that can be used in any
        part of the query. """
        stmt = aliased(Statement)
        ctx = aliased(Context)
        q = q.filter(stmt.context_id == ctx.id)
        q = q.filter(stmt.dataset_id == self.dataset.id)
        q = q.filter(ctx.active == True) # noqa
        return stmt, q

    def filter_value(self, q, stmt):
        q = q.filter(stmt._value == self.node.value)
        return q

    def filter(self, q, stmt):
        """ Apply filters to the given query recursively. """
        if not self.node.filtered:
            return q

        filter_stmt, q = self._add_statement(q)
        q = q.filter(stmt.subject == filter_stmt.subject)

        if self.node.attribute:
            q = q.filter(stmt._attribute == self.node.attribute.name)

        if self.node.leaf:
            return self.filter_value(q, filter_stmt)

        for child in self.children:
            q = child.filter(q, stmt)
        return q

    def filter_query(self, parents=None):
        """ An inner query that is used to apply any filters, limits
        and offset. """
        q = db.session.query()
        stmt, q = self._add_statement(q)
        q = q.add_column(stmt.subject)

        if parents is not None and self.node.attribute:
            parent_stmt, q = self._add_statement(q)
            q = q.filter(stmt.subject == parent_stmt._value)
            q = q.filter(parent_stmt._attribute == self.node.attribute.name)
            q = q.filter(parent_stmt.subject.in_(parents))

        q = self.filter(q, stmt)
        q = q.group_by(stmt.subject)
        q = q.order_by(stmt.subject.asc())

        if self.node.root:
            q = q.limit(self.node.limit)
            q = q.offset(self.node.offset)

        return q

    def nested(self):
        """ A list of all sub-entities for which separate queries will
        be conducted. """
        for child in self.children:
            if child.node.leaf or not child.node.attribute:
                continue
            if child.node.attribute.data_type == 'entity':
                yield child

    def project(self):
        """ Figure out which attributes should be returned for the current
        level of the query. """
        attrs = set()
        for child in self.children:
            if child.node.blank and child.node.leaf:
                attrs.update(child.node.attributes)
        attrs = attrs if len(attrs) else attributes
        skip_nested = [n.node.attribute for n in self.nested()]
        return [a.name for a in attrs if a not in skip_nested]

    def base_object(self, data):
        """ Make sure to return all the existing filter fields
        for query results. """
        obj = {
            'id': data.get('id'),
            'api_url': url_for('entities.view', dataset=self.dataset.slug,
                               id=data.get('id')),
            'parent_id': data.get('parent_id')
        }
        for child in self.children:
            if child.node.leaf and child.node.filtered:
                obj[child.node.name] = child.node.raw
            return obj
        return obj

    def get_node(self, name):
        """ Get the node for a given name. """
        for child in self.children:
            if child.node.name == name:
                return child.node
        return None if name == '*' else self.get_node('*')

    def data_query(self, parents=None):
        """ Generate a query for any statement which matches the criteria
        specified through the filter query. """
        filter_q = self.filter_query(parents=parents)
        q = db.session.query()
        stmt, q = self._add_statement(q)

        filter_sq = filter_q.subquery()
        q = q.filter(stmt.subject == filter_sq.c.subject)
        q = q.filter(stmt._attribute.in_(self.project()))

        q = q.add_column(stmt.subject.label('id'))
        q = q.add_column(stmt._attribute.label('attribute'))
        q = q.add_column(stmt._value.label('value'))

        if parents is not None and self.node.attribute:
            parent_stmt, q = self._add_statement(q)
            q = q.filter(stmt.subject == parent_stmt._value)
            q = q.filter(parent_stmt._attribute == self.node.attribute.name)
            q = q.add_column(parent_stmt.subject.label('parent_id'))

        q = q.order_by(filter_sq.c.subject.desc())
        q = q.order_by(stmt.created_at.asc())
        return q

    def execute(self, parents=None):
        """ Run the data query and construct entities from it's results. """
        results = {}
        for row in self.data_query(parents=parents):
            data = row._asdict()
            id = data.get('id')
            if id not in results:
                results[id] = self.base_object(data)
            value = data.get('value')
            attr = attributes[data.get('attribute')]
            if attr.data_type not in ['type', 'entity']:
                conv = attr.converter(self.dataset, attr)
                value = conv.deserialize_safe(value)

            node = self.get_node(data.get('attribute'))
            if attr.many if node is None else node.many:
                if attr.name not in results[id]:
                    results[id][attr.name] = []
                results[id][attr.name].append(value)
            else:
                results[id][attr.name] = value
        return results

    def collect(self, parents=None):
        """ Given re-constructed entities, conduct queries for child
        entities and merge them into the current level's object graph. """
        results = self.execute(parents=parents)
        ids = results.keys()
        for child in self.nested():
            attr = child.node.attribute.name
            for child_data in child.collect(parents=ids).values():
                parent_id = child_data.pop('parent_id')
                if child.node.many:
                    if attr not in results[parent_id]:
                        results[parent_id][attr] = []
                    results[parent_id][attr].append(child_data)
                else:
                    results[parent_id][attr] = child_data
        return results

    def query(self):
        results = []
        for result in self.collect().values():
            result.pop('parent_id')
            if not self.node.many:
                return result
            results.append(result)
        return results
