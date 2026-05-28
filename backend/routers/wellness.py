from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.wellness import WellnessEntry
from backend.schemas.wellness import WellnessEntryCreate, WellnessEntry
from backend.core.security import verify_token

router = APIRouter()

def get_wellness_entries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(WellnessEntry).offset(skip).limit(limit).all()

def get_wellness_entry(db: Session, entry_id: int):
    return db.query(WellnessEntry).filter(WellnessEntry.id == entry_id).first()

def create_wellness_entry(db: Session, entry: WellnessEntryCreate):
    db_entry = WellnessEntry(
        user_id=entry.user_id,
        mood=entry.mood,
        sleep_hours=entry.sleep_hours,
        exercise_minutes=entry.exercise_minutes,
        stress_level=entry.stress_level,
        notes=entry.notes
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def update_wellness_entry(db: Session, entry_id: int, entry_update: WellnessEntryCreate):
    db_entry = get_wellness_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    
    for key, value in entry_update.dict(exclude_unset=True).items():
        setattr(db_entry, key, value)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_wellness_entry(db: Session, entry_id: int):
    db_entry = get_wellness_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    
    db.delete(db_entry)
    db.commit()
    return db_entry

@router.get("/", response_model=list[WellnessEntry])
def read_wellness_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    entries = get_wellness_entries(db, skip, limit)
    return entries

@router.get("/{entry_id}", response_model=WellnessEntry)
def read_wellness_entry(entry_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_entry = get_wellness_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Wellness entry not found")
    return db_entry

@router.post("/", response_model=WellnessEntry)
def create_new_wellness_entry(entry: WellnessEntryCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return create_wellness_entry(db, entry)

@router.put("/{entry_id}", response_model=WellnessEntry)
def update_wellness_entry_endpoint(entry_id: int, entry: WellnessEntryCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return update_wellness_entry(db, entry_id, entry)

@router.delete("/{entry_id}")
def delete_wellness_entry_endpoint(entry_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return delete_wellness_entry(db, entry_id)