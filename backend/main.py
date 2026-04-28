from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from sqlalchemy import select

from app.api.routers import auth, exercises, workouts, cycles, cycle_runs, users, planned_workouts, achievements, social, notifications
from app.config import settings
from app.core.database import async_session
from app.core.ws_manager import manager
from app.domain.models import User


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
app.include_router(achievements.router, prefix="/api/achievements", tags=["achievements"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Verify JWT and resolve user
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        await websocket.close(code=4001)
        return

    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    if not user:
        await websocket.close(code=4001)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep alive: client sends ping, we pong back
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
