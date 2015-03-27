"""pairings

Revision ID: 4e016135b2d3
Revises: 41425b04ec86
Create Date: 2015-03-27 12:00:06.986425

"""

# revision identifiers, used by Alembic.
revision = '4e016135b2d3'
down_revision = '41425b04ec86'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('pairing',
    sa.Column('id', sa.String(length=25), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('left_id', sa.String(length=25), nullable=True),
    sa.Column('right_id', sa.String(length=25), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('decided', sa.Boolean(), nullable=True),
    sa.Column('decision', sa.Boolean(), nullable=True),
    sa.Column('decider_id', sa.String(length=25), nullable=True),
    sa.Column('dataset_id', sa.String(length=25), nullable=True),
    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], ),
    sa.ForeignKeyConstraint(['decider_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
