"""context enrich score

Revision ID: 18142b43de60
Revises: 172fe403f380
Create Date: 2015-04-02 16:52:57.336381

"""

# revision identifiers, used by Alembic.
revision = '18142b43de60'
down_revision = '172fe403f380'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('context', sa.Column('enrich_score', sa.Integer(), nullable=True))


def downgrade():
    pass
