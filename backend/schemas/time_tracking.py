from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TimeEntryBase(BaseModel):
    user_id: int
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    description: Optional[str] = None

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntry(TimeEntryBase):
    id: int
    duration: Optional[float] = None  # Duration in seconds
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True