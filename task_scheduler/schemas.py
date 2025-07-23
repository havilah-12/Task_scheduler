
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    task_str_id: str
    description: str
    estimated_time_minutes: int

class TaskOut(BaseModel):
    task_str_id: str
    description: str
    estimated_time_minutes: int
    status: str
    submitted_at: datetime

    class Config:
        orm_mode = True

class StatusUpdate(BaseModel):
    new_status: str
