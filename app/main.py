from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.events import router as events_router
from app.routes.registrations import router as reg_router
from app.routes.teams import router as teams_router
from app.routes.projects import router as projects_router
from app.routes.evaluations import router as evaluations_router
from app.routes.mentors import router as mentors_router
app = FastAPI(title="Hackathon Platform API", version="1.0.0")

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(reg_router)
app.include_router(teams_router)
app.include_router(projects_router)
app.include_router(evaluations_router)
app.include_router(mentors_router)

@app.get("/")
def root():
    return {"message": "Hackathon Platform API is running 🚀"}