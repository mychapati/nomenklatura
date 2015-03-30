"""drop dataset

Revision ID: 462244d610f2
Revises: 4e016135b2d3
Create Date: 2015-03-30 19:13:20.108657

"""

# revision identifiers, used by Alembic.
revision = '462244d610f2'
down_revision = '4e016135b2d3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint(u'context_dataset_id_fkey', 'context', type_='foreignkey')
    op.drop_column('context', 'dataset_id')
    op.drop_constraint(u'pairing_dataset_id_fkey', 'pairing', type_='foreignkey')
    op.drop_column('pairing', 'dataset_id')
    op.drop_constraint(u'statement_dataset_id_fkey', 'statement', type_='foreignkey')
    op.drop_column('statement', 'dataset_id')
    op.add_column('user', sa.Column('system_role', sa.Unicode()))
    op.drop_table('role')
    op.drop_table('dataset')


def downgrade():
    pass
