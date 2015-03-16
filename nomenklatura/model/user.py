from datetime import datetime

from formencode import Schema, validators

from nomenklatura.core import db, url_for, login_manager
from nomenklatura.model.common import make_key


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserEditSchema(Schema):
    allow_extra_fields = True
    display_name = validators.String(min=3, max=512)
    email = validators.Email()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Unicode)
    twitter_id = db.Column(db.Unicode)
    facebook_id = db.Column(db.Unicode)
    login = db.Column(db.Unicode)
    display_name = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    api_key = db.Column(db.Unicode, default=make_key)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    datasets = db.relationship('Dataset', backref='owner',
                               lazy='dynamic')
    uploads = db.relationship('Upload', backref='creator',
                              lazy='dynamic')
    entities_created = db.relationship('Entity', backref='creator',
                                       lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'github_id': self.github_id,
            'display_name': self.display_name,
            'email': self.email,
            'login': self.login,
            'api_url': url_for('users.view', id=self.id),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User(%r,%r)>' % (self.id, self.email)

    def __unicode__(self):
        return self.display_name

    def update(self, data):
        data = UserEditSchema().to_python(data)
        self.display_name = data.get('display_name')
        self.email = data.get('email')

    @classmethod
    def all(cls):
        return cls.query

    @classmethod
    def by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def by_api_key(cls, api_key):
        return cls.query.filter_by(api_key=api_key).first()

    @classmethod
    def by_github_id(cls, github_id):
        return cls.query.filter_by(github_id=github_id).first()

    @classmethod
    def by_twitter_id(cls, twitter_id):
        return cls.query.filter_by(twitter_id=twitter_id).first()

    @classmethod
    def by_facebook_id(cls, facebook_id):
        return cls.query.filter_by(facebook_id=facebook_id).first()

    @classmethod
    def load(cls, data):
        user = None
        if 'github_id' in data:
            user = cls.by_github_id(data.get('github_id'))
        elif 'twitter_id' in data:
            user = cls.by_twitter_id(data.get('twitter_id'))
        elif 'facebook_id' in data:
            user = cls.by_facebook_id(data.get('facebook_id'))
        if user is None:
            user = cls()

        user.twitter_id = data.get('twitter_id')
        user.github_id = data.get('github_id')
        user.facebook_id = data.get('facebook_id')
        if not user.login:
            user.login = data.get('login')
        if not user.display_name:
            user.display_name = data.get('display_name')
        if not user.email:
            user.email = data.get('email')
        db.session.add(user)
        return user
