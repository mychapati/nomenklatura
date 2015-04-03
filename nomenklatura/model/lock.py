from nomenklatura.core import db
from nomenklatura.model.common import CommonMixIn


class Lock(db.Model, CommonMixIn):
    __tablename__ = 'lock'

    topic = db.Column(db.Unicode)

    def __init__(self, topic):
        self.topic = topic

    @classmethod
    def query_topic(cls, topic):
        q = db.session.query(cls)
        q = q.filter(cls.topic == topic)
        return q

    @classmethod
    def acquire(cls, topic):
        lock = cls.query_topic(topic).first()
        if lock is not None:
            return False
        lock = Lock(topic)
        db.session.add(lock)
        db.session.commit()
        return lock

    @classmethod
    def release(cls, topic):
        cls.query_topic(topic).delete()
        db.session.commit()

    def __repr__(self):
        return u'<Lock(%r)>' % (self.topic)

    def __unicode__(self):
        return self.topic
