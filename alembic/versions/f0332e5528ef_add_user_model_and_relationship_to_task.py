"""Add user model and relationship to task

Revision ID: f0332e5528ef
Revises: 60f0e778b37a
Create Date: 2026-01-14 20:45:00.595965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0332e5528ef'
down_revision: Union[str, Sequence[str], None] = '60f0e778b37a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    user_indexes = {index['name'] for index in inspector.get_indexes('users')} if 'users' in existing_tables else set()
    if 'ix_users_email' not in user_indexes:
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
    if 'ix_users_id' not in user_indexes:
        op.create_index('ix_users_id', 'users', ['id'])

    if 'tasks' in existing_tables:
        task_columns = {column['name'] for column in inspector.get_columns('tasks')}
        task_fks = inspector.get_foreign_keys('tasks')
        has_owner_fk = any(
            fk.get('name') == 'fk_tasks_owner_id_users'
            or (
                fk.get('referred_table') == 'users'
                and fk.get('constrained_columns') == ['owner_id']
            )
            for fk in task_fks
        )
        needs_owner_column = 'owner_id' not in task_columns
        needs_owner_fk = not has_owner_fk

        if needs_owner_column or needs_owner_fk:
            with op.batch_alter_table('tasks') as batch_op:
                if needs_owner_column:
                    batch_op.add_column(
                        sa.Column('owner_id', sa.Integer(), nullable=True)
                    )
                if needs_owner_fk:
                    batch_op.create_foreign_key(
                        'fk_tasks_owner_id_users',
                        'users',
                        ['owner_id'],
                        ['id']
                    )

def downgrade() -> None:
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.drop_constraint(
            'fk_tasks_owner_id_users',
            type_='foreignkey'
        )
        batch_op.drop_column('owner_id')

    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

