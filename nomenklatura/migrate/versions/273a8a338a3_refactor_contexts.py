"""refactor contexts

Revision ID: 273a8a338a3
Revises: 53952c86700f
Create Date: 2015-03-22 19:55:57.633535

"""

# revision identifiers, used by Alembic.
revision = '273a8a338a3'
down_revision = '53952c86700f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('context', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('context', sa.Column('source_url', sa.Unicode(), nullable=True))
    op.add_column('context', sa.Column('user_id', sa.String(length=25), nullable=True))
    op.create_foreign_key(None, 'context', 'user', ['user_id'], ['id'])
    op.drop_column('context', 'url')
    op.drop_column('context', 'user_submitted')


def downgrade():
    pass
