from nomenklatura.core import db
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH


class Context(db.Model, CommonMixIn):
    """ A context isolates statements found at a particular source. It
    therefore establishes a grouping for entities as they are generated
    by the spiders. """

    __tablename__ = 'context'

    source_url = db.Column(db.Unicode)
    publisher = db.Column(db.Unicode)
    publisher_url = db.Column(db.Unicode)
    active = db.Column(db.Boolean)

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
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'source_url': self.source_url,
            'active': self.active,
            'user_id': self.user_id,
            'publisher': self.publisher,
            'publisher_url': self.publisher_url
        }

    def __repr__(self):
        return u'<Context(%r, %r)>' % (self.id, self.source_url)

    def __unicode__(self):
        return self.id
