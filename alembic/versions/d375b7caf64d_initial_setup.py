"""initial_setup

Revision ID: d375b7caf64d
Revises: 
Create Date: 2026-02-14 04:03:48.943794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'd375b7caf64d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create base tables: users, vehicles, service_records."""
    # Users table
    op.create_table('users',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('is_banned', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Vehicles table
    op.create_table('vehicles',
        sa.Column('vin', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('mileage', sa.Integer(), server_default='0', nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('vin')
    )
    op.create_index(op.f('ix_vehicles_vin'), 'vehicles', ['vin'], unique=False)

    # Service records table (base columns only — extra columns added in later migration)
    op.create_table('service_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicle_vin', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_vin'], ['vehicles.vin'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_records_id'), 'service_records', ['id'], unique=False)


def downgrade() -> None:
    """Drop base tables."""
    op.drop_index(op.f('ix_service_records_id'), table_name='service_records')
    op.drop_table('service_records')
    op.drop_index(op.f('ix_vehicles_vin'), table_name='vehicles')
    op.drop_table('vehicles')
    op.drop_table('users')

