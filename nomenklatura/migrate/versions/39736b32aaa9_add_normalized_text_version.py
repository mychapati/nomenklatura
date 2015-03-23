"""add normalized text version

Revision ID: 39736b32aaa9
Revises: 2777ef4e38b9
Create Date: 2015-03-23 22:06:32.879909

"""

# revision identifiers, used by Alembic.
revision = '39736b32aaa9'
down_revision = '2777ef4e38b9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('statement', sa.Column('normalized', sa.Unicode(), nullable=True))


def downgrade():
    pass
