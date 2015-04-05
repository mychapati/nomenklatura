import os
import yaml
from glob import glob

from nomenklatura.core import db, FIXTURES
from nomenklatura.processing.imports import store_upload, analyze_upload
from nomenklatura.processing.imports import load_upload


def import_fixture(model_file, data_file):
    with open(data_file, 'rb') as dfh:
        context = store_upload(dfh, data_file, None)

    analyze_upload(context.id)

    with open(model_file, 'rb') as fh:
        model = yaml.load(fh)
        context.update(model)
    db.session.commit()
    load_upload(context.id)


def import_fixtures():
    path = os.path.join(FIXTURES, 'data', '*.yaml')
    for model_file in glob(path):
        data_file = model_file.replace('.yaml', '.csv')
        import_fixture(model_file, data_file)
