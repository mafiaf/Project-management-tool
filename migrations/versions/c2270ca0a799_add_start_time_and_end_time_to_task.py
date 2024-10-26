from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Revision identifiers, used by Alembic.
revision = 'c2270ca0a799'
down_revision = '23ebc3a1f493'
branch_labels = None
depends_on = None

def upgrade():
    # Add the columns, temporarily allowing nulls
    with op.batch_alter_table('task') as batch_op:
        batch_op.add_column(sa.Column('start_time', sa.DateTime(), nullable=True, default=datetime.utcnow))
        batch_op.add_column(sa.Column('end_time', sa.DateTime(), nullable=True))

    # Populate the start_time field for existing rows with the current time
    op.execute('UPDATE task SET start_time = CURRENT_TIMESTAMP')

    # Now that the column has been populated, make it non-nullable
    with op.batch_alter_table('task') as batch_op:
        batch_op.alter_column('start_time', nullable=False)

def downgrade():
    # Downgrade logic to remove the columns
    with op.batch_alter_table('task') as batch_op:
        batch_op.drop_column('start_time')
        batch_op.drop_column('end_time')
