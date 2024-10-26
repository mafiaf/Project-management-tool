"""Add purpose, priority, and due_date fields to Task model

Revision ID: 51ca25f52bcb
Revises: c2270ca0a799
Create Date: 2024-10-26 16:08:59.232162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51ca25f52bcb'
down_revision = 'c2270ca0a799'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('task') as batch_op:
        batch_op.add_column(sa.Column('purpose', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.String(length=50), nullable=False, server_default='Medium'))
        batch_op.add_column(sa.Column('due_date', sa.DateTime(), nullable=True))

def downgrade():
    with op.batch_alter_table('task') as batch_op:
        batch_op.drop_column('due_date')
        batch_op.drop_column('priority')
        batch_op.drop_column('purpose')



    # ### end Alembic commands ###
