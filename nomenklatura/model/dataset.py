from nomenklatura.core import db, url_for
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH
from nomenklatura.model.role import Role
from nomenklatura.model.query import EntityQuery
from nomenklatura.model.forms import DatasetCreateForm
from nomenklatura.model.forms import DatasetEditForm


class Dataset(db.Model, CommonMixIn):
    __tablename__ = 'dataset'

    slug = db.Column(db.Unicode)
    label = db.Column(db.Unicode)
    public = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('user.id'))

    roles = db.relationship('Role', backref='dataset',
                            lazy='dynamic')

    @property
    def entities(self):
        return EntityQuery(dataset=self)

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'api_url': url_for('datasets.view', dataset=self.slug),
            'label': self.label,
            'owner': self.owner.to_dict(),
            'public': self.public,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first()

    @classmethod
    def all(cls):
        return cls.query

    @classmethod
    def create(cls, data, user):
        data = DatasetCreateForm().deserialize(data)
        dataset = cls()
        dataset.owner = user
        dataset.slug = data['slug']
        dataset.label = data['label']
        db.session.add(dataset)
        db.session.flush()
        Role.update({'role': Role.MANAGE, 'user': user}, dataset)
        return dataset

    def update(self, data):
        data = DatasetEditForm().deserialize(data)
        self.label = data['label']
        self.public = data['public']
        db.session.add(self)
        db.session.flush()
