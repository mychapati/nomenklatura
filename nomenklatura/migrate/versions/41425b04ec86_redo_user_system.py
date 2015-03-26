"""redo user system

Revision ID: 41425b04ec86
Revises: 1fc452ca254d
Create Date: 2015-03-26 16:07:48.394456

"""

# revision identifiers, used by Alembic.
revision = '41425b04ec86'
down_revision = '1fc452ca254d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils.types.password import PasswordType


def upgrade():
    op.drop_column('dataset', 'ignore_case')
    op.drop_column('dataset', 'normalize_text')
    op.drop_column('dataset', 'enable_invalid')
    op.drop_column('dataset', 'match_aliases')
    op.add_column('user', sa.Column('password', PasswordType(), nullable=True))
    op.add_column('user', sa.Column('validated', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('validation_token', sa.Unicode(), nullable=True))
    op.drop_column('user', 'login')
    op.drop_column('user', 'twitter_id')
    op.drop_column('user', 'github_id')
    op.drop_column('user', 'facebook_id')


def downgrade():
    pass
