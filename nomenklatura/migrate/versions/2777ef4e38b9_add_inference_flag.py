"""add inference flag

Revision ID: 2777ef4e38b9
Revises: 273a8a338a3
Create Date: 2015-03-23 16:20:02.626864

"""

# revision identifiers, used by Alembic.
revision = '2777ef4e38b9'
down_revision = '273a8a338a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('statement', sa.Column('inferred', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_statement_attribute'), 'statement', ['attribute'], unique=False)
    op.create_index(op.f('ix_statement_subject'), 'statement', ['subject'], unique=False)
    op.create_index(op.f('ix_statement_value'), 'statement', ['value'], unique=False)


def downgrade():
    pass
