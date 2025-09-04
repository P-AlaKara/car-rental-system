"""Add unique constraint for payments idempotency

Revision ID: add_payments_idempotency_constraint
Revises: add_handover_fields
Create Date: 2025-09-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payments_idempotency_constraint'
down_revision = 'add_handover_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create a partial unique index where gateway is 'payadvantage' and gateway_transaction_id is not null
    # For SQLite compatibility in tests, also create a non-partial unique index if partial indexes unsupported
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind else ''
    if dialect_name == 'postgresql':
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_payments_gateway_txn_payadvantage
            ON payments (booking_id, gateway, gateway_transaction_id)
            WHERE gateway = 'payadvantage' AND gateway_transaction_id IS NOT NULL
            """
        )
    else:
        # Fallback unique index (will enforce uniqueness across all gateways when txn id present)
        op.create_unique_constraint(
            'uq_payments_gateway_txn_booking',
            'payments',
            ['booking_id', 'gateway', 'gateway_transaction_id']
        )


def downgrade():
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind else ''
    if dialect_name == 'postgresql':
        op.execute("DROP INDEX IF EXISTS uq_payments_gateway_txn_payadvantage")
    else:
        op.drop_constraint('uq_payments_gateway_txn_booking', 'payments', type_='unique')

