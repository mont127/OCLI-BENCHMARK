from fastapi import FastAPI
from backend.routers import users, tasks, projects, time_tracking, wellness
from backend.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Remote Work Productivity Platform")

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(time_tracking.router, prefix="/api/time", tags=["time_tracking"])
app.include_router(wellness.router, prefix="/api/wellness", tags=["wellness"])

@app.get("/")
async def root():
    return {"message": "Remote Work Productivity Platform API"}