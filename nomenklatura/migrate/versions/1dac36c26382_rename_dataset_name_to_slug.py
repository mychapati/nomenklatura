"""rename dataset name to slug

Revision ID: 1dac36c26382
Revises: 3ba3875e1c58
Create Date: 2015-03-18 10:30:03.071029

"""

# revision identifiers, used by Alembic.
revision = '1dac36c26382'
down_revision = '3ba3875e1c58'

from alembic import op
# import sqlalchemy as sa


def upgrade():
    op.alter_column('dataset', 'name', new_column_name='slug')


def downgrade():
    pass
