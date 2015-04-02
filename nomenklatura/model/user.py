from passlib.hash import sha256_crypt

from nomenklatura.core import db, app, url_for, login_manager
from nomenklatura.model.constants import ROLES
from nomenklatura.model.forms import UserEditForm, UserCreateForm
from nomenklatura.model.common import CommonMixIn, make_key


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, CommonMixIn):
    __tablename__ = 'user'

    display_name = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    password = db.Column(db.Unicode)
    system_role = db.Column(db.Enum(*ROLES, name='roles'), nullable=False)
    validated = db.Column(db.Boolean, default=False)
    validation_token = db.Column(db.Unicode, default=make_key)
    api_key = db.Column(db.Unicode, default=make_key)

    def to_dict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'system_role': self.system_role,
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
        if data.get('password') is not None:
            self.password = sha256_crypt.encrypt(data.get('password'))

    def verify(self, password):
        if password is None or self.password is None:
            return False
        return sha256_crypt.verify(password, self.password)

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
        user.system_role = app.config.get('DEFAULT_USER_ROLE')
        user.password = sha256_crypt.encrypt(data.get('password'))
        db.session.add(user)
        return user
