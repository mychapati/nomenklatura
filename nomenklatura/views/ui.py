import os

from apikit.jsonify import JSONEncoder
from flask import render_template

from nomenklatura.core import app, app_name, app_title
from nomenklatura.schema import types


def angular_templates():
    partials_dir = os.path.join(app.static_folder, 'templates')
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as fh:
                sub_path = file_path[len(partials_dir) + 1:]
                yield ('/static/templates/%s' % sub_path,
                       fh.read().decode('utf-8'))


@app.route('/entities')
@app.route('/entities/<path:id>')
@app.route('/imports')
@app.route('/imports/<path:id>')
@app.route('/settings')
@app.route('/manage')
@app.route('/manage/<path:id>')
@app.route('/review')
@app.route('/login')
@app.route('/docs/<path:id>')
@app.route('/')
def index(**kw):
    config = JSONEncoder().encode({
        'NAME': app_name,
        'TITLE': app_title,
        'SCHEMA': {
            'types': types
        }
    })
    return render_template('app.html', config=config,
                           app_name=app_name, app_title=app_title,
                           angular_templates=angular_templates())
