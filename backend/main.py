from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import workouts, exercises, user

app = FastAPI(title="GymDiary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["exercises"])
app.include_router(user.router, prefix="/api/user", tags=["user"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
