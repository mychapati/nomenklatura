"""add role

Revision ID: 3daf7dd8941b
Revises: 1dac36c26382
Create Date: 2015-03-21 14:21:10.735554

"""

# revision identifiers, used by Alembic.
revision = '3daf7dd8941b'
down_revision = '1dac36c26382'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('read', 'write', 'manage', name='roles'), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    ) # noqa


def downgrade():
    pass
