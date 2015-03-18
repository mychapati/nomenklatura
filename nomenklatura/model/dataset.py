from datetime import datetime

from nomenklatura.core import db
from nomenklatura.model.forms import DatasetNewSchema
from nomenklatura.model.forms import DatasetEditSchema


class Dataset(db.Model):
    __tablename__ = 'dataset'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Unicode)
    label = db.Column(db.Unicode)
    ignore_case = db.Column(db.Boolean, default=False)
    match_aliases = db.Column(db.Boolean, default=False)
    public_edit = db.Column(db.Boolean, default=False)
    normalize_text = db.Column(db.Boolean, default=True)
    enable_invalid = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    entities = db.relationship('Entity', backref='dataset',
                               lazy='dynamic')
    uploads = db.relationship('Upload', backref='dataset',
                              lazy='dynamic')
    roles = db.relationship('Role', backref='dataset',
                            lazy='dynamic')

    def to_dict(self):
        from nomenklatura.model.entity import Entity
        num_aliases = Entity.all(self).filter(Entity.canonical_id != None).count()
        num_review = Entity.all(self).filter_by(reviewed=False).count()
        num_entities = Entity.all(self).count()
        num_invalid = Entity.all(self).filter_by(invalid=True).count()

        return {
            'id': self.id,
            'slug': self.slug,
            'label': self.label,
            'owner': self.owner.to_dict(),
            'stats': {
                'num_aliases': num_aliases,
                'num_entities': num_entities,
                'num_review': num_review,
                'num_invalid': num_invalid
            },
            'ignore_case': self.ignore_case,
            'match_aliases': self.match_aliases,
            'public_edit': self.public_edit,
            'normalize_text': self.normalize_text,
            'enable_invalid': self.enable_invalid,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first()

    @classmethod
    def find_slugs(cls):
        q = db.session.query(cls.slug)
        return q

    @classmethod
    def all(cls):
        return cls.query

    @classmethod
    def create(cls, data, user):
        data = DatasetNewSchema().to_python(data)
        dataset = cls()
        dataset.owner = user
        dataset.slug = data['slug']
        dataset.label = data['label']
        db.session.add(dataset)
        db.session.flush()
        return dataset

    def update(self, data):
        data = DatasetEditSchema().to_python(data)
        self.label = data['label']
        self.normalize_text = data['normalize_text']
        self.ignore_case = data['ignore_case']
        self.public_edit = data['public_edit']
        self.match_aliases = data['match_aliases']
        self.enable_invalid = data['enable_invalid']
        db.session.add(self)
        db.session.flush()
