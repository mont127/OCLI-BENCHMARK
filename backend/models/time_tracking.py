from sqlalchemy import Column, Integer, DateTime, ForeignKey, Interval, Float
from backend.core.database import Base
from datetime import datetime

class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Interval)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)