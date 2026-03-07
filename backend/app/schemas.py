from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class AuthRegister(BaseModel):
    email: str
    password: str
    name: str


class AuthLogin(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str


# ---------------------------------------------------------------------------
# Exercise
# ---------------------------------------------------------------------------

class ExerciseCreate(BaseModel):
    name: str
    muscleGroup: str
    secondaryMuscles: list[str] = []
    equipment: str
    description: str = ""


class ExerciseOut(BaseModel):
    id: str
    name: str
    muscleGroup: str
    secondaryMuscles: list[str]
    equipment: str
    description: str
    isCustom: bool


# ---------------------------------------------------------------------------
# Sets / WorkoutExercise
# ---------------------------------------------------------------------------

class SetIn(BaseModel):
    weight: float = 0.0
    reps: int = 0
    completed: bool = False


class SetOut(BaseModel):
    id: str
    weight: float
    reps: int
    completed: bool


class WorkoutExerciseIn(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: list[SetIn] = []


class WorkoutExerciseOut(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: list[SetOut]


# ---------------------------------------------------------------------------
# Workout
# ---------------------------------------------------------------------------

class WorkoutCreate(BaseModel):
    date: date
    type: str
    title: str
    durationMinutes: int = 0
    notes: str = ""
    exercises: list[WorkoutExerciseIn] = []


class WorkoutUpdate(BaseModel):
    date: Optional[date] = None
    type: Optional[str] = None
    title: Optional[str] = None
    durationMinutes: Optional[int] = None
    notes: Optional[str] = None
    exercises: Optional[list[WorkoutExerciseIn]] = None


class WorkoutOut(BaseModel):
    id: str
    date: date
    type: str
    title: str
    durationMinutes: int
    notes: str
    createdAt: datetime
    exercises: list[WorkoutExerciseOut]


# ---------------------------------------------------------------------------
# User / Profile
# ---------------------------------------------------------------------------

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    avatarUrl: Optional[str] = None


class WeightEntryIn(BaseModel):
    date: date
    kg: float


class WeightEntryOut(BaseModel):
    date: date
    kg: float


class GoalCreate(BaseModel):
    text: str
    targetDate: Optional[date] = None
    done: bool = False


class GoalOut(BaseModel):
    id: str
    text: str
    targetDate: Optional[date]
    done: bool


class UserOut(BaseModel):
    name: str
    age: int
    avatarUrl: Optional[str]
    weightLog: list[WeightEntryOut]
    goals: list[GoalOut]
