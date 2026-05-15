from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas, models, database, ai_service

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

@router.get("/", response_model=List[schemas.Device])
def list_devices(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    db_devices = db.query(models.Device).offset(skip).limit(limit).all()
    
    # Enrich devices with health data
    for dev in db_devices:
        telemetry_data = db.query(models.Telemetry).filter(models.Telemetry.device_id == dev.id).order_by(models.Telemetry.timestamp.desc()).limit(50).all()
        if telemetry_data:
            analysis = ai_service.predict_device_health(telemetry_data)
            # Add latest raw data for UI display convenience
            analysis["gas_level"] = telemetry_data[0].gas_level
            analysis["pressure"] = telemetry_data[0].pressure
            analysis["soda_lime"] = telemetry_data[0].soda_lime
            dev.health = analysis
        else:
            dev.health = {
                "health_score": 100,
                "status": "Active",
                "is_healthy": True,
                "malfunction_probability": 0.0,
                "issues": [],
                "insights": [],
                "prediction": "System Stable",
                "gas_level": 35.0,
                "pressure": 32.0,
                "soda_lime": 100.0
            }
            
    return db_devices

@router.post("/", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(database.get_db)):
    # Auto-entry simulation: If name is generic or missing, assign smart name
    if "New" in device.name or not device.name:
        device.name = f"Smart-Unit-{device.type}-{device.location}"
        
    db_device = models.Device(
        name=device.name,
        type=device.type,
        location=device.location,
        status=device.status,
        room_id=device.room_id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    # Trigger arrival notification
    arrival_notif = models.Notification(
        device_id=db_device.id,
        receiver_type="Technician",
        message=f"New device {db_device.name} has arrived and registered at {db_device.location}."
    )
    db.add(arrival_notif)
    db.commit()
    
    return db_device


@router.get("/{device_id}", response_model=schemas.Device)
def get_device(device_id: int, db: Session = Depends(database.get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.post("/{device_id}/telemetry", response_model=schemas.Telemetry)
def add_telemetry(device_id: int, telemetry: schemas.TelemetryCreate, db: Session = Depends(database.get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db_telemetry = models.Telemetry(
        device_id=device_id,
        pressure=telemetry.pressure,
        flow_rate=telemetry.flow_rate,
        gas_level=telemetry.gas_level,
        battery_level=telemetry.battery_level
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

@router.get("/{device_id}/health")
def get_device_health(device_id: int, db: Session = Depends(database.get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get last 50 telemetry points for analysis
    telemetry_data = db.query(models.Telemetry).filter(models.Telemetry.device_id == device_id).order_by(models.Telemetry.timestamp.desc()).limit(50).all()
    
    # Run AI analysis
    analysis = ai_service.predict_device_health(telemetry_data)
    
    # Auto-generate notifications for critical insights
    if not analysis["is_healthy"] or analysis["malfunction_probability"] > 0.7:
        for insight in analysis["insights"]:
            # Check if this exact notification was recently sent to avoid spam (simple check)
            recent_notif = db.query(models.Notification).filter(
                models.Notification.device_id == device_id,
                models.Notification.message == insight,
                models.Notification.is_read == False
            ).first()
            
            if not recent_notif:
                new_notif = models.Notification(
                    device_id=device_id,
                    receiver_type="Doctor" if "Emergency" in insight or "Blood" in insight else "Technician",
                    message=insight
                )
                db.add(new_notif)
        db.commit()

    return {
        "device_id": device_id,
        "device_name": device.name,
        "analysis": analysis
    }
