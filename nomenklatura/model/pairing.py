from datetime import datetime
from sqlalchemy import or_, and_

from nomenklatura.core import db, types
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH
from nomenklatura.model.forms import PairingForm
from nomenklatura.model.statement import Statement
from nomenklatura.model.context import Context


class Pairing(db.Model, CommonMixIn):
    __tablename__ = 'pairing'

    left_id = db.Column(db.String(KEY_LENGTH))
    right_id = db.Column(db.String(KEY_LENGTH))

    score = db.Column(db.Integer, default=None, nullable=True)
    decided = db.Column(db.Boolean, default=False, nullable=False)
    decision = db.Column(db.Boolean, default=None, nullable=True)
    decider_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('user.id'),
                           nullable=True)
    decider = db.relationship('User', backref=db.backref('pairings',
                              lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'left_id': self.left_id,
            'right_id': self.right_id,
            'score': self.score,
            'decided': self.decided,
            'decision': self.decision,
            'decider_id': self.decider_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def all(cls):
        return cls.query

    def apply(self):
        same_as = types.Node.attributes.same_as.qname
        if not self.decided:
            return
        q = db.session.query(Statement)
        q = q.filter(Statement.attribute == same_as)
        q = q.filter(or_(
            and_(Statement.subject == self.left_id,
                 Statement._value == self.right_id),
            and_(Statement.subject == self.right_id,
                 Statement._value == self.left_id)
        ))
        stmt = q.first()
        if self.decision is True and stmt is None:
            context = Context.create(self.decider, {})
            stmt = Statement(self.left_id, same_as, self.right_id, context)
            db.session.add(context)
            db.session.add(stmt)

        if self.decision is False and stmt is not None:
            stmt.deleted_at = datetime.utcnow()

    @classmethod
    def update(cls, data, user, score=None):
        data = PairingForm().deserialize(data)
        entities = data.get('left_id'), data.get('right_id')
        left_id, right_id = min(entities), max(entities)
        q = cls.all()
        q = q.filter_by(left_id=left_id).filter_by(right_id=right_id)
        pairing = q.first()
        if pairing is None:
            pairing = cls()
            pairing.left_id = left_id
            pairing.right_id = right_id

        if score is not None:
            pairing.score = score

        pairing.decision = data.get('decision')
        if pairing.decision in [True, False]:
            pairing.decided = True
            pairing.decider = user
        else:
            pairing.decided = False
            pairing.decider = None

        db.session.add(pairing)
        return pairing

    @classmethod
    def existing(cls, entity_id):
        q = cls.all()
        q = q.filter(or_(cls.left_id == entity_id,
                         cls.right_id == entity_id))
        for pairing in q:
            if pairing.left_id == entity_id:
                yield pairing.right_id
            else:
                yield pairing.left_id
