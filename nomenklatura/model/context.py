from nomenklatura.core import db
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH


class Context(db.Model, CommonMixIn):
    """ A context isolates statements found at a particular source. It
    therefore establishes a grouping for entities as they are generated
    by the spiders. """

    __tablename__ = 'context'

    url = db.Column(db.Unicode)
    publisher = db.Column(db.Unicode)
    publisher_url = db.Column(db.Unicode)
    user_submitted = db.Column(db.Boolean)

    dataset_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('contexts',
                              lazy='dynamic', cascade='all, delete-orphan')) # noqa

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'url': self.url,
            'user_submitted': self.user_submitted,
            'publisher': self.publisher,
            'publisher_url': self.publisher_url
        }

    def __repr__(self):
        return u'<Context(%r, %r)>' % (self.id, self.url)

    def __unicode__(self):
        return self.id
