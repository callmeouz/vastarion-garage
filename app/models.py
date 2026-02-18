from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="driver")
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vehicle(Base):
    __tablename__ = "vehicles"

    vin = Column(String, primary_key=True, index=True)
    model = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, server_default="0", nullable=False)
    color = Column(String, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)

class VehicleAccess(Base):
    __tablename__ = "vehicle_access"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_vin = Column(String, ForeignKey("vehicles.vin", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission = Column(String, default="viewer", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ServiceRecord(Base):
    __tablename__ = "service_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_vin = Column(String, ForeignKey("vehicles.vin", ondelete="CASCADE"), nullable=False)

    description = Column(String, nullable=False)
    mileage = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=True)
    service_name = Column(String, nullable=True)

    date = Column(DateTime(timezone=True), server_default=func.now())