from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b64723ccf546'
down_revision = '554dedb3ad6c'
branch_labels = None
depends_on = None

def upgrade():
    # Alter 'task' table to add the category_id column
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_task_category_id',  # Provide a name for the foreign key constraint
            'category',
            ['category_id'],
            ['id']
        )

def downgrade():
    # Reverse the upgrade steps
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('fk_task_category_id', type_='foreignkey')
        batch_op.drop_column('category_id')
