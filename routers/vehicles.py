from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud
from app.database import get_db
from app.dependencies import get_current_user
from uuid import UUID

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)

@router.post("/", response_model=schemas.VehicleOut)
def create_vehicle(
    vehicle: schemas.VehicleCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)

@router.get("/my-vehicles", response_model=List[schemas.VehicleOut])
def read_my_vehicles(
    skip: int = 0,
    limit: int = 20,
    brand: Optional[str] = None,
    sort: str = "-year",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_vehicles(
        db=db, 
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        brand=brand,
        sort=sort
    )

@router.get("/shared-with-me")
def shared_with_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_shared_vehicles(db=db, user_id=current_user.id)

@router.put("/{vin}", response_model=schemas.VehicleOut)
def update_vehicle(
    vin: str,
    update_data: schemas.VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    vehicle = crud.update_vehicle(db=db, vehicle_vin=vin, user_id=current_user.id, update_data=update_data)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya güncelleme yetkiniz yok.")
    return vehicle

@router.delete("/{vin}")
def delete_vehicle(
    vin: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_vehicle(db, vehicle_vin=vin, user_id=current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya silme yetkiniz yok")
    return {"message": "Araç başarıyla garajdan çıkarıldı"}

@router.post("/{vin}/share")
def share_vehicle(
    vin: str, 
    share_data: schemas.ShareVehicleCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vin == vin, 
        models.Vehicle.owner_id == current_user.id
    ).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya bu aracı paylaşma yetkiniz yok.")
    
    target_user = crud.get_user_by_email(db, email=share_data.email)
    if not target_user:
        raise HTTPException(status_code=404, detail="Bu email adresiyle kayıtlı bir kullanıcı bulunamadı.")
        
    if target_user.id == current_user.id:
         raise HTTPException(status_code=400, detail="Kendi aracınızı kendinize paylaşamazsınız.")
    
    access = crud.share_vehicle(
        db=db, 
        vehicle_vin=vin, 
        target_user_id=target_user.id, 
        permission=share_data.permission
    )
    return {"message": f"Araç başarıyla {share_data.email} kullanıcısına '{share_data.permission}' yetkisiyle paylaşıldı."}

@router.get("/{vin}/access", response_model=List[schemas.VehicleAccessOutWithEmail])
def get_vehicle_access_list(
    vin: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.vin == vin, models.Vehicle.owner_id == current_user.id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya yetkiniz yok.")
        
    return crud.get_vehicle_accesses(db=db, vehicle_vin=vin)

@router.delete("/{vin}/access/{target_user_id}")
def remove_vehicle_access(
    vin: str, 
    target_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    vehicle = db.query(models.Vehicle).filter(models.Vehicle.vin == vin, models.Vehicle.owner_id == current_user.id).first()
    if not vehicle:
         raise HTTPException(status_code=404, detail="Araç bulunamadı veya yetkiniz yok.")

    success = crud.revoke_vehicle_access(db=db, vehicle_vin=vin, target_user_id=target_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bu kullanıcının bu araçta zaten bir yetkisi yok.")
        
    return {"message": "Kullanıcının araç üzerindeki yetkisi tamamen kaldırıldı."}

# --- SERVİS GEÇMİŞİ ENDPOINT'LERİ ---

def _can_access_vehicle(db: Session, vin: str, user_id, required_permissions: list = None):
    """Aracın sahibi mi yoksa yetkili kullanıcı mı kontrol et."""
    # Önce owner mı kontrol et
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vin == vin,
        models.Vehicle.owner_id == user_id,
        models.Vehicle.is_deleted == False
    ).first()
    if vehicle:
        return vehicle, "owner"
    
    # Değilse, VehicleAccess tablosunu kontrol et
    if required_permissions:
        access = db.query(models.VehicleAccess).filter(
            models.VehicleAccess.vehicle_vin == vin,
            models.VehicleAccess.user_id == user_id,
            models.VehicleAccess.permission.in_(required_permissions)
        ).first()
        if access:
            vehicle = db.query(models.Vehicle).filter(
                models.Vehicle.vin == vin,
                models.Vehicle.is_deleted == False
            ).first()
            if vehicle:
                return vehicle, access.permission
    
    return None, None

@router.post("/{vin}/service-records", response_model=schemas.ServiceRecordOut)
def create_service_record(
    vin: str,
    record: schemas.ServiceRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    vehicle, role = _can_access_vehicle(db, vin, current_user.id, ["editor", "driver"])
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya bu araca servis kaydı ekleme yetkiniz yok.")
        
    return crud.add_service_record(db=db, vehicle_vin=vin, record=record)

@router.get("/{vin}/service-records", response_model=List[schemas.ServiceRecordOut])
def get_service_records(
    vin: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    vehicle, role = _can_access_vehicle(db, vin, current_user.id, ["viewer", "editor", "driver"])
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya yetkiniz yok.")
        
    return crud.get_service_records(db=db, vehicle_vin=vin)

@router.delete("/{vin}/service-records/{record_id}")
def delete_service_record(
    vin: str,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    vehicle, role = _can_access_vehicle(db, vin, current_user.id, ["editor"])
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Araç bulunamadı veya silme yetkiniz yok.")
    
    success = crud.delete_service_record(db=db, record_id=record_id, vehicle_vin=vin)
    if not success:
        raise HTTPException(status_code=404, detail="Servis kaydı bulunamadı.")
    
    return {"message": "Servis kaydı silindi."}
