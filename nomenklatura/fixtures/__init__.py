import os
from glob import glob

from nomenklatura.core import FIXTURES
from nomenklatura.processing.imports import import_file_sync


def import_fixtures():
    path = os.path.join(FIXTURES, 'data', '*.yaml')
    for model_file in glob(path):
        data_file = model_file.replace('.yaml', '.csv')
        import_file_sync(model_file, data_file)
