"""change uploads model

Revision ID: 1fc452ca254d
Revises: 39736b32aaa9
Create Date: 2015-03-24 12:30:11.523877

"""

# revision identifiers, used by Alembic.
revision = '1fc452ca254d'
down_revision = '39736b32aaa9'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.drop_table('upload')
    op.add_column('context', sa.Column('resource_mapping',
                  sqlalchemy_utils.types.json.JSONType(), nullable=True))
    op.add_column('context', sa.Column('resource_name', sa.Unicode(),
                  nullable=True))


def downgrade():
    pass
