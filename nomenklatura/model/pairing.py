from sqlalchemy import or_

from nomenklatura.core import db
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH
from nomenklatura.model.forms import PairingForm
from nomenklatura.model.schema import attributes


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

    dataset_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('pairings',
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

    @classmethod
    def update(cls, data, dataset, user, score=None):
        data = PairingForm().deserialize(data)
        entities = data.get('left_id'), data.get('right_id')
        left_id, right_id = min(entities), max(entities)
        q = cls.all().filter_by(dataset=dataset)
        q = q.filter_by(left_id=left_id).filter_by(right_id=right_id)
        pairing = q.first()
        if pairing is None:
            pairing = cls()
            pairing.dataset = dataset
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
    def existing(cls, dataset, entity_id):
        q = cls.all().filter_by(dataset=dataset)
        q = q.filter(or_(cls.left_id == entity_id,
                         cls.right_id == entity_id))
        for pairing in q:
            if pairing.left_id == entity_id:
                yield pairing.right_id
            else:
                yield pairing.left_id

    @classmethod
    def next(cls, dataset, exclude=None):
        q = cls.all().filter_by(dataset=dataset)
        q = q.filter_by(decided=False)
        if exclude is not None:
            q = q.filter(cls.id != exclude)
        q = q.order_by(cls.score.desc())

        next_ = q.first()
        if next_ is None:
            next_ = cls.generate(dataset)
        return next_

    @classmethod
    def generate(cls, dataset, num_rounds=10, cutoff=90):
        best_pair = None
        best_score = 0
        for i in range(num_rounds):
            ent = dataset.entities.random()
            avoid = [ent.id] + list(cls.existing(dataset, ent.id))
            for label in [ent.label] + ent.get(attributes.alias):
                q = dataset.entities.not_subject(avoid).levenshtein(label)
                q = q.no_same_as().limit(1)
                for score, otr in q.scored():
                    if score >= cutoff:
                        return cls.update({
                            'left_id': otr.id,
                            'right_id': ent.id
                        }, dataset, None, score=score)
                    if score > best_score:
                        best_score = score
                        best_pair = (ent, otr)

        if best_pair is not None:
            return cls.update({
                'left_id': best_pair[0].id,
                'right_id': best_pair[1].id
            }, dataset, None, score=best_score)
