from flask import Blueprint
from apikit import jsonify

from nomenklatura.schema import attributes, types


blueprint = Blueprint('schema', __name__)


@blueprint.route('/schema')
def schema():
    return jsonify({
        'attributes': attributes._items,
        'types': types._items
    })
