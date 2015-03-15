"""rename account to user

Revision ID: 1c74cb54ea0a
Revises: 3ab0816749b4
Create Date: 2015-03-15 19:34:51.819890

"""

# revision identifiers, used by Alembic.
revision = '1c74cb54ea0a'
down_revision = '3ab0816749b4'

from alembic import op
# import sqlalchemy as sa
# from sqlalchemy.dialects import postgresql


def upgrade():
    op.rename_table('account', 'user')
    op.drop_constraint(u'dataset_owner_id_fkey', 'dataset', type_='foreignkey')
    op.create_foreign_key(None, 'dataset', 'user', ['owner_id'], ['id'])
    op.drop_constraint(u'entity_creator_id_fkey', 'entity', type_='foreignkey')
    op.create_foreign_key(None, 'entity', 'user', ['creator_id'], ['id'])
    op.drop_constraint(u'upload_creator_id_fkey', 'upload', type_='foreignkey')
    op.create_foreign_key(None, 'upload', 'user', ['creator_id'], ['id'])


def downgrade():
    pass
