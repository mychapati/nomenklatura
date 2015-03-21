from datetime import datetime

from nomenklatura.core import db


class Role(db.Model):
    __tablename__ = 'role'

    READ = 'read'
    WRITE = 'write'
    MANAGE = 'manage'
    ROLES = [READ, WRITE, MANAGE]

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Enum(*ROLES, name='roles'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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
