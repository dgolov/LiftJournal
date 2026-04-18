from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, exercises, workouts, cycles, cycle_runs, users, planned_workouts


app = FastAPI(title="LiftJournal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["exercises"])
app.include_router(users.router, prefix="/api/user", tags=["user"])
app.include_router(cycles.router, prefix="/api/cycles", tags=["cycles"])
app.include_router(cycle_runs.router, prefix="/api", tags=["cycle-runs"])
app.include_router(planned_workouts.router, prefix="/api/planned-workouts", tags=["planned-workouts"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
