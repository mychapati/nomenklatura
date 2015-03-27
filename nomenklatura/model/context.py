from sqlalchemy_utils.types.json import JSONType

from nomenklatura.core import db, url_for
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH
from nomenklatura.model.forms import ContextEditForm


class Context(db.Model, CommonMixIn):
    """ A context isolates statements found at a particular source. It
    therefore establishes a grouping for entities as they are generated
    by the spiders. """

    __tablename__ = 'context'

    source_url = db.Column(db.Unicode)
    publisher = db.Column(db.Unicode)
    publisher_url = db.Column(db.Unicode)
    active = db.Column(db.Boolean, default=True)

    resource_name = db.deferred(db.Column(db.Unicode))
    resource_mapping = db.deferred(db.Column(JSONType))

    dataset_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('contexts',
                              lazy='dynamic', cascade='all, delete-orphan')) # noqa

    user_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('user.id'),
                        nullable=True)
    user = db.relationship('User', backref=db.backref('contexts',
                           lazy='dynamic', cascade='all, delete-orphan')) # noqa

    def to_dict(self):
        return {
            'id': self.id,
            'api_url': url_for('contexts.view', dataset=self.dataset.slug, id=self.id),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'source_url': self.source_url,
            'resource_name': self.resource_name,
            'active': self.active,
            'user_id': self.user_id,
            'publisher': self.publisher,
            'publisher_url': self.publisher_url
        }

    @classmethod
    def by_id(cls, id, dataset=None):
        q = db.session.query(cls)
        q = q.filter(cls.id == id)
        if dataset is not None:
            q = q.filter(cls.dataset == dataset)
        return q.first()

    @classmethod
    def create(cls, dataset, user, data):
        ctx = cls()
        ctx.user = user
        ctx.dataset = dataset
        ctx.update(data)
        return ctx

    def update(self, data):
        data = ContextEditForm().deserialize(data)
        self.active = data.get('active')
        self.source_url = data.get('source_url')
        self.publisher = data.get('publisher')
        self.publisher_url = data.get('publisher_url')
        if data.get('resource_name') is not None:
            self.resource_name = data.get('resource_name')
        if data.get('resource_mapping') is not None:
            self.resource_mapping = data.get('resource_mapping')
        db.session.add(self)

    def __repr__(self):
        return u'<Context(%r, %r)>' % (self.id, self.source_url)

    def __unicode__(self):
        return self.id
