from nomenklatura.core import db
from nomenklatura.model.forms import RoleForm
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH


class Role(db.Model, CommonMixIn):
    __tablename__ = 'role'

    READ = 'read'
    EDIT = 'edit'
    MANAGE = 'manage'
    NONE = 'none'
    ROLES = [READ, EDIT, MANAGE]

    role = db.Column(db.Enum(*ROLES, name='roles'), nullable=False)
    dataset_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('dataset.id'))
    user_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('user.id'))

    @classmethod
    def update(cls, data, dataset):
        data = RoleForm().deserialize(data)
        q = db.session.query(cls)
        q = q.filter(cls.user == data.get('user'))
        q = q.filter(cls.dataset == dataset)
        role = q.first()
        if data.get('role') == 'none':
            if role is None:
                return
            db.session.delete(role)
        else:
            if role is None:
                role = cls()
                role.user = data.get('user')
                role.dataset = dataset
            role.role = data.get('role')
            db.session.add(role)
            return role

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'dataset_id': self.dataset_id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def all(cls):
        return cls.query
