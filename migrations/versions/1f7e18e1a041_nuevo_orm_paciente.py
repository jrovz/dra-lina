"""Nuevo orm paciente

Revision ID: 1f7e18e1a041
Revises: efdf28ad8441
Create Date: 2026-02-17 08:32:09.218205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f7e18e1a041'
down_revision = 'efdf28ad8441'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_id', sa.String(length=30), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=False, server_default='0'))
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.create_unique_constraint('uq_patient_document_id', ['document_id'])


def downgrade():
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.drop_constraint('uq_patient_document_id', type_='unique')
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
        batch_op.drop_column('age')
        batch_op.drop_column('document_id')
