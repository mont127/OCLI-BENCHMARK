from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.project import Project
from backend.schemas.project import ProjectCreate, Project
from backend.core.security import verify_token

router = APIRouter()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def create_project(db: Session, project: ProjectCreate, user_id: int):
    db_project = Project(
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        created_by=user_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_update: ProjectCreate):
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return db_project

@router.get("/", response_model=list[Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    projects = get_projects(db, skip, limit)
    return projects

@router.get("/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.post("/", response_model=Project)
def create_new_project(project: ProjectCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    # Verify the user exists
    from backend.routers.users import get_user
    user = get_user(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return create_project(db, project, user.id)

@router.put("/{project_id}", response_model=Project)
def update_project_endpoint(project_id: int, project: ProjectCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return update_project(db, project_id, project)

@router.delete("/{project_id}")
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    return delete_project(db, project_id)