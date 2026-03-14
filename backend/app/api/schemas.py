from datetime import date, datetime
from typing import Optional

_Date = date  # alias to avoid field-name shadowing in Pydantic models

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
    date: Optional[_Date] = None
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


class UserMaxIn(BaseModel):
    exercise_name: str
    weight_kg: float


class UserMaxOut(BaseModel):
    exercise_name: str
    weight_kg: float
    recorded_at: date


class UserOut(BaseModel):
    name: str
    age: int
    avatarUrl: Optional[str]
    weightLog: list[WeightEntryOut]
    goals: list[GoalOut]
    maxes: list[UserMaxOut] = []


# ---------------------------------------------------------------------------
# Training cycles
# ---------------------------------------------------------------------------

class CycleSetIn(BaseModel):
    percent_1rm: float
    reps: int


class CycleSetOut(BaseModel):
    id: str
    percent_1rm: float
    reps: int
    order: int


class CycleExerciseIn(BaseModel):
    exercise_id: Optional[str] = None
    exercise_name: str
    sets: list[CycleSetIn] = []


class CycleExerciseOut(BaseModel):
    id: str
    exercise_id: Optional[str] = None
    exercise_name: str
    sets: list[CycleSetOut]


class CycleWorkoutIn(BaseModel):
    workout_number: int
    title: str = ""
    notes: str = ""
    exercises: list[CycleExerciseIn] = []


class CycleWorkoutOut(BaseModel):
    id: str
    workout_number: int
    title: str
    notes: str
    exercises: list[CycleExerciseOut]


class CycleCreate(BaseModel):
    title: str
    description: str = ""
    author_name: str = ""
    is_public: bool = False
    workouts: list[CycleWorkoutIn] = []


class CycleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author_name: Optional[str] = None
    is_public: Optional[bool] = None
    workouts: Optional[list[CycleWorkoutIn]] = None


class CycleListOut(BaseModel):
    id: str
    title: str
    description: str
    author_name: str
    created_by: int
    is_public: bool
    created_at: datetime
    workout_count: int


class CycleDetailOut(BaseModel):
    id: str
    title: str
    description: str
    author_name: str
    created_by: int
    is_public: bool
    created_at: datetime
    workouts: list[CycleWorkoutOut]


# ---------------------------------------------------------------------------
# Cycle runs
# ---------------------------------------------------------------------------

class CycleWorkoutLogOut(BaseModel):
    id: str
    cycle_workout_id: str
    workout_id: Optional[str]
    completed_at: Optional[datetime]


class CycleRunOut(BaseModel):
    id: str
    cycle_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    logs: list[CycleWorkoutLogOut]


class StartCycleWorkoutIn(BaseModel):
    notes: str = ""


class CompleteWorkoutIn(BaseModel):
    workout_id: Optional[str] = None
