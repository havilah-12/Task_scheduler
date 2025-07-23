
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    if task.estimated_time_minutes <= 0:
        raise HTTPException(status_code=400, detail="Estimated time must be > 0")
    if db.query(models.Task).filter_by(task_str_id=task.task_str_id).first():
        raise HTTPException(status_code=400, detail="task_str_id must be unique")
    
    new_task = models.Task(
        task_str_id=task.task_str_id,
        description=task.description,
        estimated_time_minutes=task.estimated_time_minutes,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_str_id}", response_model=schemas.TaskOut)
def get_task(task_str_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter_by(task_str_id=task_str_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_str_id}/status", response_model=schemas.TaskOut)
def update_status(task_str_id: str, status: schemas.StatusUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter_by(task_str_id=task_str_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    valid = ["pending", "processing", "completed"]
    if status.new_status not in valid:
        raise HTTPException(status_code=400, detail="Invalid status")

    if task.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot change status of completed task")
    if task.status == "processing" and status.new_status == "pending":
        raise HTTPException(status_code=400, detail="Cannot revert processing to pending")

    task.status = status.new_status
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks/next-to-process", response_model=schemas.TaskOut)
def next_task(db: Session = Depends(get_db)):
    task = (
        db.query(models.Task)
        .filter_by(status="pending")
        .order_by(models.Task.estimated_time_minutes, models.Task.submitted_at)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="No pending task")
    return task

@app.get("/tasks/pending", response_model=list[schemas.TaskOut])
def list_pending(sort_by: str = "estimated_time_minutes", order: str = "asc", limit: int = 10, db: Session = Depends(get_db)):
    valid_sort = {"estimated_time_minutes": models.Task.estimated_time_minutes, "submitted_at": models.Task.submitted_at}
    if sort_by not in valid_sort:
        raise HTTPException(status_code=400, detail="Invalid sort_by value")

    sort_col = valid_sort[sort_by]
    order_func = sort_col.asc() if order == "asc" else sort_col.desc()

    tasks = (
        db.query(models.Task)
        .filter_by(status="pending")
        .order_by(order_func)
        .limit(limit)
        .all()
    )
    return tasks
