from sqlalchemy import or_, and_

from nomenklatura.core import db
from nomenklatura.schema import attributes
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

    def apply(self):
        if not self.decided:
            return
        q = db.session.query(Statement)
        q = q.filter(Statement.dataset == self.dataset)
        q = q.filter(Statement._attribute == attributes.same_as.name)
        q = q.filter(or_(
            and_(Statement.subject == self.left_id,
                 Statement._value == self.right_id),
            and_(Statement.subject == self.right_id,
                 Statement._value == self.left_id)
        ))
        stmt = q.first()
        if self.decision is True and stmt is None:
            context = Context.create(self.dataset, self.decider, {})
            stmt = Statement(self.dataset, self.left_id, attributes.same_as,
                             self.right_id, context)
            db.session.add(context)
            db.session.add(stmt)

        # TODO: figure out how to delete a statement.

        if stmt is not None:
            from nomenklatura.processing import process_updates
            process_updates.delay(self.dataset.slug, statement_id=stmt.id)

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
    def generate(cls, dataset, num_rounds=15, cutoff=90):
        from nomenklatura.query import execute_query
        best_pair = None
        best_score = 0
        for i in range(num_rounds):
            query = {
                'label': None,
                'sort': 'random',
                'same_as': {'optional': 'forbidden'}
            }
            ent = execute_query(dataset, query).get('result')
            ent_id = ent.get('id')
            avoid = [ent_id] + list(cls.existing(dataset, ent_id))
            q = {
                'id|!=': avoid,
                'label%=': ent.get('label'),
                'same_as': {'optional': 'forbidden'},
                '!same_as': {'optional': 'forbidden', 'id': ent_id}
            }
            for res in execute_query(dataset, [q]).get('result'):
                if res.get('score') >= cutoff:
                    return cls.update({
                        'left_id': res.get('id'),
                        'right_id': ent_id
                    }, dataset, None, score=res.get('score'))
                if res.get('score') > best_score:
                    best_score = res.get('score')
                    best_pair = (ent_id, res.get('id'))

        if best_pair is not None:
            return cls.update({
                'left_id': best_pair[0],
                'right_id': best_pair[1]
            }, dataset, None, score=best_score)
