from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from backend.core.database import engine, get_db
from backend.core.security import verify_password, get_password_hash
from backend.models import user, task, project, time_tracking, wellness
from backend.schemas.user import UserCreate, UserLogin, UserOut
from backend.schemas.task import TaskCreate, TaskUpdate
from backend.schemas.project import ProjectCreate, ProjectUpdate
from backend.schemas.time_tracking import TimeEntryCreate, TimeEntryUpdate
from backend.schemas.wellness import WellnessEntryCreate, WellnessEntryUpdate

# Create tables
user.Base.metadata.create_all(bind=engine)
task.Base.metadata.create_all(bind=engine)
project.Base.metadata.create_all(bind=engine)
time_tracking.Base.metadata.create_all(bind=engine)
wellness.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Remote Work Productivity Platform API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Include routers
from backend.routers import users, tasks, projects, time_tracking, wellness
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(time_tracking.router, prefix="/time-entries", tags=["time_entries"])
app.include_router(wellness.router, prefix="/wellness-entries", tags=["wellness_entries"])

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Return the main index.html file
    try:
        with open("frontend/index.html", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "<h1>Frontend not found</h1>"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)