
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, models, database

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@router.get("/", response_model=List[schemas.Notification])
def list_notifications(receiver_type: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Notification)
    if receiver_type:
        query = query.filter(models.Notification.receiver_type == receiver_type)
    return query.order_by(models.Notification.timestamp.desc()).all()

@router.post("/read/{notif_id}")
def mark_read(notif_id: int, db: Session = Depends(database.get_db)):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="لم يتم العثور على الإشعار")
    notif.is_read = True
    db.commit()
    return {"status": "نجاح"}
