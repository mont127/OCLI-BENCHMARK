from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text, Float
from backend.core.database import Base
from datetime import datetime

class WellnessEntry(Base):
    __tablename__ = "wellness_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mood = Column(Integer)  # Scale of 1-10
    sleep_hours = Column(Float)
    exercise_minutes = Column(Integer)
    stress_level = Column(Integer)  # Scale of 1-10
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)