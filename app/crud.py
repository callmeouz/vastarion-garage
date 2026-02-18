from sqlalchemy.orm import Session
from . import models, schemas, utils
from uuid import UUID
from sqlalchemy import desc

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = utils.hash_password(user.password)
    
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_pwd
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate, user_id: UUID):
    db_vehicle = models.Vehicle(**vehicle.model_dump(), owner_id=user_id)
    
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def get_user_vehicles(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 20, 
    brand: str = None, 
    sort: str = "-year"
):
    query = db.query(models.Vehicle).filter(
        models.Vehicle.owner_id == user_id,
        models.Vehicle.is_deleted == False
    )
    
    if brand:
        query = query.filter(models.Vehicle.brand.ilike(f"%{brand}%"))
        
    if sort == "-year":
        query = query.order_by(desc(models.Vehicle.year))
    elif sort == "year":
        query = query.order_by(models.Vehicle.year)

    return query.offset(skip).limit(limit).all()

def delete_vehicle(db: Session, vehicle_vin: str, user_id: UUID):
    db_vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vin == vehicle_vin, 
        models.Vehicle.owner_id == user_id
    ).first()
    
    if db_vehicle:
        db_vehicle.is_deleted = True 
        db.commit()
        return True
        
    return False

def update_vehicle(db: Session, vehicle_vin: str, user_id: UUID, update_data: schemas.VehicleUpdate):
    db_vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vin == vehicle_vin, 
        models.Vehicle.owner_id == user_id,
        models.Vehicle.is_deleted == False
    ).first()
    if db_vehicle:
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(db_vehicle, field, value)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle
    return None

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not utils.verify_password(password, user.hashed_password):
        return False
    return user

# --- ARAÇ PAYLAŞIM (ACCESS) İŞLEMLERİ ---

def share_vehicle(db: Session, vehicle_vin: str, target_user_id: UUID, permission: str):
    existing_access = db.query(models.VehicleAccess).filter(
        models.VehicleAccess.vehicle_vin == vehicle_vin,
        models.VehicleAccess.user_id == target_user_id
    ).first()

    if existing_access:
        existing_access.permission = permission 
        db.commit()
        db.refresh(existing_access)
        return existing_access

    new_access = models.VehicleAccess(
        vehicle_vin=vehicle_vin,
        user_id=target_user_id,
        permission=permission
    )
    db.add(new_access)
    db.commit()
    db.refresh(new_access)
    return new_access

def get_vehicle_accesses(db: Session, vehicle_vin: str):
    rows = (
        db.query(models.VehicleAccess, models.User.email)
        .join(models.User, models.User.id == models.VehicleAccess.user_id)
        .filter(models.VehicleAccess.vehicle_vin == vehicle_vin)
        .all()
    )

    return [
        {
            "id": access.id,
            "vehicle_vin": access.vehicle_vin,
            "user_id": access.user_id,
            "email": email,
            "permission": access.permission,
        }
        for (access, email) in rows
    ]

def revoke_vehicle_access(db: Session, vehicle_vin: str, target_user_id: UUID):
    access = db.query(models.VehicleAccess).filter(
        models.VehicleAccess.vehicle_vin == vehicle_vin,
        models.VehicleAccess.user_id == target_user_id
    ).first()
    
    if access:
        db.delete(access)
        db.commit()
        return True
    return False

# --- SERVİS GEÇMİŞİ İŞLEMLERİ ---

def add_service_record(db: Session, vehicle_vin: str, record: schemas.ServiceRecordCreate):
    # Yeni bir servis kaydı oluştur
    db_record = models.ServiceRecord(
        vehicle_vin=vehicle_vin,
        **record.model_dump()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_service_records(db: Session, vehicle_vin: str):
    # Bir aracın tüm servis geçmişini tarihe göre yeniden eskiye (desc) sıralayarak getir
    return db.query(models.ServiceRecord).filter(
        models.ServiceRecord.vehicle_vin == vehicle_vin
    ).order_by(models.ServiceRecord.date.desc()).all()

def delete_service_record(db: Session, record_id: int, vehicle_vin: str):
    record = db.query(models.ServiceRecord).filter(
        models.ServiceRecord.id == record_id,
        models.ServiceRecord.vehicle_vin == vehicle_vin
    ).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

def get_shared_vehicles(db: Session, user_id: UUID):
    rows = (
        db.query(
            models.Vehicle,
            models.VehicleAccess.permission,
            models.User.email.label("owner_email")
        )
        .join(models.VehicleAccess, models.VehicleAccess.vehicle_vin == models.Vehicle.vin)
        .join(models.User, models.User.id == models.Vehicle.owner_id)  # ✅ owner join
        .filter(models.VehicleAccess.user_id == user_id)
        .filter(models.Vehicle.is_deleted == False)
        .all()
    )

    return [
        {
            "vin": v.vin,
            "brand": v.brand,
            "model": v.model,
            "year": v.year,
            "mileage": v.mileage,
            "color": v.color,
            "owner_id": v.owner_id,
            "created_at": v.created_at,
            "permission": perm,
            "owner_email": owner_email,
        }
        for (v, perm, owner_email) in rows
    ]