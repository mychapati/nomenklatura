from sqlalchemy_utils.types.password import PasswordType

from nomenklatura.core import db, url_for, login_manager
from nomenklatura.model.forms import UserEditForm, UserCreateForm
from nomenklatura.model.common import CommonMixIn, make_key


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, CommonMixIn):
    __tablename__ = 'user'

    display_name = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    password_ = db.Column('password', PasswordType)
    validated = db.Column(db.Boolean, default=False)
    validation_token = db.Column(db.Unicode, default=make_key)
    api_key = db.Column(db.Unicode, default=make_key)

    datasets = db.relationship('Dataset', backref='owner',
                               lazy='dynamic')

    roles = db.relationship('Role', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'email': self.email,
            'api_url': url_for('users.view', id=self.id),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def is_active(self):
        return self.validated

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
        data = UserEditForm().deserialize(data)
        self.display_name = data.get('display_name')
        self.email = data.get('email')
        if data.get('password'):
            self.password = data.get('password')

    @classmethod
    def all(cls):
        return cls.query

    @classmethod
    def by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def by_api_key(cls, api_key):
        return cls.query.filter_by(api_key=api_key).first()

    @classmethod
    def create(cls, data):
        data = UserCreateForm().deserialize(data)
        user = cls()
        user.display_name = data.get('display_name')
        user.email = data.get('email')
        user.password = data.get('password')
        db.session.add(user)
        return user
