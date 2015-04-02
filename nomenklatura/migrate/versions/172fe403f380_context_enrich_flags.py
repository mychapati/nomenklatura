"""context enrich flags

Revision ID: 172fe403f380
Revises: 41f413316fb6
Create Date: 2015-04-02 16:41:48.186879

"""

# revision identifiers, used by Alembic.
revision = '172fe403f380'
down_revision = '41f413316fb6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('context', sa.Column('enrich_root', sa.Unicode(length=25), nullable=True))
    states = sa.Enum('pending', 'accepted', 'rejected', name='states')
    bind = op.get_bind()
    impl = states.dialect_impl(bind.dialect)
    impl.create(bind, checkfirst=True)
    op.add_column('context', sa.Column('enrich_status', states, nullable=True))


def downgrade():
    pass
