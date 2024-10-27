"""Add new fields to Category model and update relationships

Revision ID: b1e0d10a867d
Revises: 8fcc1d32767b
Create Date: 2024-10-27 13:38:05.765918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1e0d10a867d'
down_revision = '8fcc1d32767b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority_level', sa.Enum('Low', 'Medium', 'High', name='priority_levels'), nullable=True))
        batch_op.add_column(sa.Column('visibility', sa.Enum('Public', 'Private', name='visibility_levels'), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('is_shared', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('icon', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('default_reminders', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_column('archived')
        batch_op.drop_column('default_reminders')
        batch_op.drop_column('icon')
        batch_op.drop_column('is_shared')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('visibility')
        batch_op.drop_column('priority_level')

    # ### end Alembic commands ###
