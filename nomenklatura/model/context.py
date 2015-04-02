from sqlalchemy_utils.types.json import JSONType

from nomenklatura.core import db, url_for
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH
from nomenklatura.model.constants import STATES
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

    enrich_root = db.deferred(db.Column(db.Unicode(KEY_LENGTH), nullable=True))
    enrich_status = db.Column(db.Enum(*STATES, name='states'), nullable=True)
    enrich_score = db.Column(db.Integer, default=None, nullable=True)

    user_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('user.id'),
                        nullable=True)
    user = db.relationship('User', backref=db.backref('contexts',
                           lazy='dynamic', cascade='all, delete-orphan')) # noqa

    def to_dict(self, enrich=False):
        data = {
            'id': self.id,
            'api_url': url_for('contexts.view', id=self.id),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'source_url': self.source_url,
            'resource_name': self.resource_name,
            'active': self.active,
            'user_id': self.user_id,
            'publisher': self.publisher,
            'publisher_url': self.publisher_url
        }
        if enrich:
            data['enrich_root'] = self.enrich_root
            data['enrich_status'] = self.enrich_status
            data['enrich_score'] = self.enrich_score
        return data

    @classmethod
    def create(cls, user, data):
        ctx = cls()
        ctx.user = user
        ctx.update(data)
        return ctx

    @classmethod
    def by_root(cls, root):
        q = db.session.query(Context)
        q = q.filter(Context.enrich_root == root)
        q = q.order_by(Context.enrich_score.desc())
        return q

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
        if data.get('enrich_root') is not None:
            self.enrich_root = data.get('enrich_root')
        if data.get('enrich_status') is not None:
            self.enrich_status = data.get('enrich_status')
        if data.get('enrich_score') is not None:
            self.enrich_score = data.get('enrich_score')
        db.session.add(self)

    def __repr__(self):
        return u'<Context(%r, %r)>' % (self.id, self.source_url)

    def __unicode__(self):
        return self.id
