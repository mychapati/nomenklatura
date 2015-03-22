from nomenklatura.core import db, url_for
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH
from nomenklatura.model.role import Role
from nomenklatura.model.forms import DatasetCreateForm
from nomenklatura.model.forms import DatasetEditForm


class Dataset(db.Model, CommonMixIn):
    __tablename__ = 'dataset'

    slug = db.Column(db.Unicode)
    label = db.Column(db.Unicode)
    ignore_case = db.Column(db.Boolean, default=False)
    match_aliases = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=False)
    normalize_text = db.Column(db.Boolean, default=True)
    enable_invalid = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('user.id'))

    uploads = db.relationship('Upload', backref='dataset',
                              lazy='dynamic')
    roles = db.relationship('Role', backref='dataset',
                            lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'api_url': url_for('datasets.view', dataset=self.slug),
            'label': self.label,
            'owner': self.owner.to_dict(),
            'ignore_case': self.ignore_case,
            'match_aliases': self.match_aliases,
            'public': self.public,
            'normalize_text': self.normalize_text,
            'enable_invalid': self.enable_invalid,
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
        self.normalize_text = data['normalize_text']
        self.ignore_case = data['ignore_case']
        self.match_aliases = data['match_aliases']
        self.enable_invalid = data['enable_invalid']
        db.session.add(self)
        db.session.flush()
