from flask.ext.script import Manager

from nomenklatura.core import app, db
from nomenklatura.model import *
from nomenklatura import views

manager = Manager(app)


@manager.command
def createdb():
    """ Make the database. """
    db.create_all()


@manager.command
def postproc_20131119():
    from nomenklatura.model.text import normalize_text
    for entity in Entity.query:
        print [entity]
        entity.normalized = normalize_text(entity.name)
        #entity.attributes = entity.data
        db.session.add(entity)
        db.session.commit()


@manager.command
def cluster(dataset):
    ds = Dataset.by_name(dataset)
    from nomenklatura.model.cluster import generate_clusters
    generate_clusters(ds)


if __name__ == '__main__':
    manager.run()

