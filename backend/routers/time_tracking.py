from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.time_tracking import TimeEntry
from backend.schemas.time_tracking import TimeEntryCreate, TimeEntry
from backend.core.security import verify_token
from datetime import datetime

router = APIRouter()

def get_time_entries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TimeEntry).offset(skip).limit(limit).all()

def get_time_entry(db: Session, entry_id: int):
    return db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()

def create_time_entry(db: Session, time_entry: TimeEntryCreate):
    db_time_entry = TimeEntry(
        user_id=time_entry.user_id,
        task_id=time_entry.task_id,
        project_id=time_entry.project_id,
        start_time=time_entry.start_time,
        end_time=time_entry.end_time,
        description=time_entry.description
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

def update_time_entry(db: Session, entry_id: int, time_entry_update: TimeEntryCreate):
    db_time_entry = get_time_entry(db, entry_id)
    if not db_time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    for key, value in time_entry_update.dict(exclude_unset=True).items():
        setattr(db_time_entry, key, value)
    
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

def delete_time_entry(db: Session, entry_id: int):
    db_time_entry = get_time_entry(db, entry_id)
    if not db_time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    db.delete(db_time_entry)
    db.commit()
    return db_time_entry

@router.get("/", response_model=list[TimeEntry])
def read_time_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    entries = get_time_entries(db, skip, limit)
    return entries

@router.get("/{entry_id}", response_model=TimeEntry)
def read_time_entry(entry_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_entry = get_time_entry(db, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return db_entry

@router.post("/", response_model=TimeEntry)
def create_new_time_entry(time_entry: TimeEntryCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return create_time_entry(db, time_entry)

@router.put("/{entry_id}", response_model=TimeEntry)
def update_time_entry_endpoint(entry_id: int, time_entry: TimeEntryCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return update_time_entry(db, entry_id, time_entry)

@router.delete("/{entry_id}")
def delete_time_entry_endpoint(entry_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return delete_time_entry(db, entry_id)