"""redo schema

Revision ID: 3a41ad602c32
Revises: None
Create Date: 2015-04-04 11:43:27.325499

"""

# revision identifiers, used by Alembic.
revision = '3a41ad602c32'
down_revision = None

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.create_table('user',
    sa.Column('id', sa.String(length=25), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('display_name', sa.Unicode(), nullable=True),
    sa.Column('email', sa.Unicode(), nullable=False),
    sa.Column('password', sa.Unicode(), nullable=True),
    sa.Column('system_role', sa.Enum('read', 'edit', 'manage', name='roles'), nullable=False),
    sa.Column('validated', sa.Boolean(), nullable=True),
    sa.Column('validation_token', sa.Unicode(), nullable=True),
    sa.Column('api_key', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('lock',
    sa.Column('id', sa.String(length=25), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('topic', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('context',
    sa.Column('id', sa.String(length=25), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('source_url', sa.Unicode(), nullable=True),
    sa.Column('publisher', sa.Unicode(), nullable=True),
    sa.Column('publisher_url', sa.Unicode(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('resource_name', sa.Unicode(), nullable=True),
    sa.Column('resource_mapping', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('enrich_root', sa.Unicode(length=25), nullable=True),
    sa.Column('enrich_status', sa.Enum('pending', 'accepted', 'rejected', name='states'), nullable=True),
    sa.Column('enrich_score', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.String(length=25), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pairing',
    sa.Column('id', sa.String(length=25), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('left_id', sa.String(length=25), nullable=True),
    sa.Column('right_id', sa.String(length=25), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('decided', sa.Boolean(), nullable=False),
    sa.Column('decision', sa.Boolean(), nullable=True),
    sa.Column('decider_id', sa.String(length=25), nullable=True),
    sa.ForeignKeyConstraint(['decider_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('statement',
    sa.Column('id', sa.String(length=25), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('subject', sa.String(length=25), nullable=False),
    sa.Column('attribute', sa.String(length=1024), nullable=False),
    sa.Column('value', sa.Unicode(), nullable=True),
    sa.Column('normalized', sa.Unicode(), nullable=True),
    sa.Column('inferred_via', sa.String(length=100), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('context_id', sa.String(length=25), nullable=False),
    sa.ForeignKeyConstraint(['context_id'], ['context.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_statement_attribute'), 'statement', ['attribute'], unique=False)
    op.create_index(op.f('ix_statement_subject'), 'statement', ['subject'], unique=False)
    op.create_index(op.f('ix_statement_value'), 'statement', ['value'], unique=False)


def downgrade():
    pass
