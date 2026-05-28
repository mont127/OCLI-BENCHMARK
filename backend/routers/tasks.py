from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.task import Task
from backend.schemas.task import TaskCreate, Task
from backend.core.security import verify_token

router = APIRouter()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def create_task(db: Session, task: TaskCreate, user_id: int):
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=task.project_id,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        created_by=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: TaskCreate):
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return db_task

@router.get("/", response_model=list[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    tasks = get_tasks(db, skip, limit)
    return tasks

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.post("/", response_model=Task)
def create_new_task(task: TaskCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    # Verify the user exists
    from backend.routers.users import get_user
    user = get_user(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return create_task(db, task, user.id)

@router.put("/{task_id}", response_model=Task)
def update_task_endpoint(task_id: int, task: TaskCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return update_task(db, task_id, task)

@router.delete("/{task_id}")
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return delete_task(db, task_id)