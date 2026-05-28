from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WellnessEntryBase(BaseModel):
    user_id: int
    mood: Optional[int] = None  # Scale of 1-10
    sleep_hours: Optional[float] = None
    exercise_minutes: Optional[int] = None
    stress_level: Optional[int] = None  # Scale of 1-10
    notes: Optional[str] = None

class WellnessEntryCreate(WellnessEntryBase):
    pass

class WellnessEntry(WellnessEntryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True