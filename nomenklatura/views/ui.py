import os

from flask import render_template

from nomenklatura.core import app


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
@app.route('/review')
@app.route('/login')
@app.route('/docs/<path:id>')
@app.route('/')
def index(**kw):
    return render_template('app.html', angular_templates=angular_templates())
