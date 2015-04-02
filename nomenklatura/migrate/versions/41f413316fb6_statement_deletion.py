"""statement deletion

Revision ID: 41f413316fb6
Revises: 462244d610f2
Create Date: 2015-04-01 23:15:58.294787

"""

# revision identifiers, used by Alembic.
revision = '41f413316fb6'
down_revision = '462244d610f2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('statement', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('statement', sa.Column('inferred_via', sa.String(length=100), nullable=True))
    op.drop_column('statement', 'inferred')


def downgrade():
    pass
