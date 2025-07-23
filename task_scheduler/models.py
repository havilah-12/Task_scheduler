
from sqlalchemy import Column, String, Integer, Enum, DateTime
from sqlalchemy.sql import func
from database import Base
import enum

class StatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_str_id = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    estimated_time_minutes = Column(Integer)
    status = Column(Enum(StatusEnum), default="pending")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
