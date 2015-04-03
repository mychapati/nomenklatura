"""add lock model

Revision ID: 32f8037a0dc
Revises: 18142b43de60
Create Date: 2015-04-02 21:15:14.923734

"""

# revision identifiers, used by Alembic.
revision = '32f8037a0dc'
down_revision = '18142b43de60'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('lock',
        sa.Column('id', sa.String(length=25), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('topic', sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
