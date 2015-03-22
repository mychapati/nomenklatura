"""rename public_edit field

Revision ID: 26ee4f4aa633
Revises: 3daf7dd8941b
Create Date: 2015-03-22 11:50:49.263382

"""

# revision identifiers, used by Alembic.
revision = '26ee4f4aa633'
down_revision = '3daf7dd8941b'

from alembic import op


def upgrade():
    op.alter_column('dataset', 'public_edit', new_column_name='public')


def downgrade():
    pass
