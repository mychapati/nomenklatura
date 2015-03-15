"""add auth types

Revision ID: 3ba3875e1c58
Revises: 1c74cb54ea0a
Create Date: 2015-03-15 20:13:30.856977

"""

# revision identifiers, used by Alembic.
revision = '3ba3875e1c58'
down_revision = '1c74cb54ea0a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('display_name', sa.Unicode(), nullable=True))
    op.add_column('user', sa.Column('facebook_id', sa.Unicode(), nullable=True))
    op.add_column('user', sa.Column('twitter_id', sa.Unicode(), nullable=True))


def downgrade():
    pass
