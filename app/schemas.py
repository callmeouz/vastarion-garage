from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 karakter")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Şifre en az 6 karakter olmalıdır")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Şifre en az bir harf içermelidir")
        if not re.search(r"\d", v):
            raise ValueError("Şifre en az bir rakam içermelidir")
        return v

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: str = "driver"
    is_banned: bool
    created_at: datetime

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    vin: str = Field(..., min_length=4, max_length=17)
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    year: int = Field(..., gt=1885, lt=datetime.now().year + 2)
    mileage: int = Field(0, ge=0)
    color: Optional[str] = None

class VehicleCreate(VehicleBase): 
    pass

class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(None, gt=1885, lt=datetime.now().year + 2)
    mileage: Optional[int] = Field(None, ge=0)
    color: Optional[str] = None

class VehicleOut(VehicleBase):
    owner_id: UUID
    created_at: datetime
    owner_email: Optional[str] = None
    permission: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ShareVehicleCreate(BaseModel):
    email: EmailStr
    permission: str = Field(default="viewer", pattern="^(viewer|editor|driver)$")

class VehicleAccessOut(BaseModel):
    id: int
    vehicle_vin: str
    user_id: UUID
    permission: str

    class Config:
        from_attributes = True

class ServiceRecordCreate(BaseModel):
    description: str = Field(..., min_length=2, description="Örn: Ağır Bakım, Yağ Değişimi")
    mileage: int = Field(..., gt=0, description="Bakıma girdiği kilometre")
    cost: Optional[int] = None
    service_name: Optional[str] = None

class ServiceRecordOut(BaseModel):
    id: int
    vehicle_vin: str
    description: str
    mileage: int
    cost: Optional[int]
    service_name: Optional[str]
    date: datetime

    class Config:
        from_attributes = True

class VehicleAccessOutWithEmail(BaseModel):
    id: int
    vehicle_vin: str
    user_id: UUID
    email: EmailStr
    permission: str

    class Config:
        from_attributes = True