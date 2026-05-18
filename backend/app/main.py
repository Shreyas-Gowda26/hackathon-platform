from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.auth import router as auth_router
from app.routes.events import router as events_router
from app.routes.registrations import router as reg_router
from app.routes.teams import router as teams_router
from app.routes.projects import router as projects_router
from app.routes.evaluations import router as evaluations_router
from app.routes.mentors import router as mentors_router
from app.routes.judges import router as judges_router
from app.routes.users import router as users_router

app = FastAPI(title="Hackathon Platform API", version="1.0.0")

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(events_router, prefix=API_PREFIX)
app.include_router(reg_router, prefix=API_PREFIX)
app.include_router(teams_router, prefix=API_PREFIX)
app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(evaluations_router, prefix=API_PREFIX)
app.include_router(mentors_router, prefix=API_PREFIX)
app.include_router(judges_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")