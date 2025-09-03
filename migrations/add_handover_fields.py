"""Add handover fields and tables

Revision ID: add_handover_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_handover_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to bookings table
    op.add_column('bookings', sa.Column('license_verified', sa.Boolean(), nullable=True, default=False))
    op.add_column('bookings', sa.Column('license_verified_at', sa.DateTime(), nullable=True))
    op.add_column('bookings', sa.Column('contract_signed_url', sa.Text(), nullable=True))
    op.add_column('bookings', sa.Column('contract_signed_at', sa.DateTime(), nullable=True))
    op.add_column('bookings', sa.Column('pickup_odometer', sa.Integer(), nullable=True))
    op.add_column('bookings', sa.Column('return_odometer', sa.Integer(), nullable=True))
    op.add_column('bookings', sa.Column('handover_completed_at', sa.DateTime(), nullable=True))
    op.add_column('bookings', sa.Column('handover_completed_by', sa.Integer(), nullable=True))
    op.add_column('bookings', sa.Column('return_completed_at', sa.DateTime(), nullable=True))
    op.add_column('bookings', sa.Column('return_completed_by', sa.Integer(), nullable=True))
    op.add_column('bookings', sa.Column('direct_debit_schedule_id', sa.String(100), nullable=True))
    
    # Create booking_photos table
    op.create_table('booking_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('photo_type', sa.String(50), nullable=False),  # 'pickup' or 'return'
        sa.Column('photo_url', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create pay_advantage_customers table
    op.create_table('pay_advantage_customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(100), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create direct_debit_schedules table
    op.create_table('direct_debit_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('upfront_amount', sa.Float(), nullable=True),
        sa.Column('upfront_date', sa.Date(), nullable=True),
        sa.Column('recurring_amount', sa.Float(), nullable=True),
        sa.Column('recurring_start_date', sa.Date(), nullable=True),
        sa.Column('frequency', sa.String(50), nullable=True),  # weekly, fortnightly, monthly
        sa.Column('end_condition_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('authorization_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('ix_booking_photos_booking_id', 'booking_photos', ['booking_id'])
    op.create_index('ix_pay_advantage_customers_user_id', 'pay_advantage_customers', ['user_id'])
    op.create_index('ix_direct_debit_schedules_booking_id', 'direct_debit_schedules', ['booking_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_direct_debit_schedules_booking_id', 'direct_debit_schedules')
    op.drop_index('ix_pay_advantage_customers_user_id', 'pay_advantage_customers')
    op.drop_index('ix_booking_photos_booking_id', 'booking_photos')
    
    # Drop tables
    op.drop_table('direct_debit_schedules')
    op.drop_table('pay_advantage_customers')
    op.drop_table('booking_photos')
    
    # Drop columns from bookings table
    op.drop_column('bookings', 'direct_debit_schedule_id')
    op.drop_column('bookings', 'return_completed_by')
    op.drop_column('bookings', 'return_completed_at')
    op.drop_column('bookings', 'handover_completed_by')
    op.drop_column('bookings', 'handover_completed_at')
    op.drop_column('bookings', 'return_odometer')
    op.drop_column('bookings', 'pickup_odometer')
    op.drop_column('bookings', 'contract_signed_at')
    op.drop_column('bookings', 'contract_signed_url')
    op.drop_column('bookings', 'license_verified_at')
    op.drop_column('bookings', 'license_verified')