from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, models, database

router = APIRouter(
    prefix="/technicians",
    tags=["technicians"]
)

@router.get("/", response_model=List[schemas.Technician])
def list_technicians(db: Session = Depends(database.get_db)):
    return db.query(models.Technician).all()

@router.post("/", response_model=schemas.Technician)
def create_technician(tech: schemas.TechnicianCreate, db: Session = Depends(database.get_db)):
    db_tech = models.Technician(**tech.dict())
    db.add(db_tech)
    db.commit()
    db.refresh(db_tech)
    return db_tech

@router.get("/{tech_id}", response_model=schemas.Technician)
def get_technician(tech_id: int, db: Session = Depends(database.get_db)):
    tech = db.query(models.Technician).filter(models.Technician.id == tech_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")
    return tech
