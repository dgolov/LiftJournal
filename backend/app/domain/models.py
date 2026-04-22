import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    muscle_group: Mapped[str] = mapped_column(String(100), nullable=False)
    secondary_muscles: Mapped[list] = mapped_column(JSON, default=list)
    equipment: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order",
    )


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    workout_id: Mapped[str] = mapped_column(
        String, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(String, nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    workout: Mapped["Workout"] = relationship("Workout", back_populates="exercises")
    sets: Mapped[list["ExerciseSet"]] = relationship(
        "ExerciseSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="ExerciseSet.order",
    )


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    workout_exercise_id: Mapped[str] = mapped_column(
        String, ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False
    )
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    failed: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    workout_exercise: Mapped["WorkoutExercise"] = relationship(
        "WorkoutExercise", back_populates="sets"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(100), default="")
    age: Mapped[int] = mapped_column(Integer, default=0)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    theme: Mapped[str] = mapped_column(String(10), default="light")

    weight_log: Mapped[list["WeightEntry"]] = relationship(
        "WeightEntry", back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        "Goal", back_populates="user", cascade="all, delete-orphan"
    )
    maxes: Mapped[list["UserMax"]] = relationship(
        "UserMax", back_populates="user", cascade="all, delete-orphan"
    )


class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), default=1
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    kg: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="weight_log")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), default=1
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="goals")


# ── Training cycles ───────────────────────────────────────────────────────────

class TrainingCycle(Base):
    __tablename__ = "training_cycles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    author_name: Mapped[str] = mapped_column(String(200), default="")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workouts: Mapped[list["CycleWorkout"]] = relationship(
        "CycleWorkout", back_populates="cycle",
        cascade="all, delete-orphan", order_by="CycleWorkout.order",
    )


class CycleWorkout(Base):
    __tablename__ = "cycle_workouts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    cycle_id: Mapped[str] = mapped_column(String, ForeignKey("training_cycles.id", ondelete="CASCADE"), nullable=False)
    workout_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)

    cycle: Mapped["TrainingCycle"] = relationship("TrainingCycle", back_populates="workouts")
    exercises: Mapped[list["CycleExercise"]] = relationship(
        "CycleExercise", back_populates="workout",
        cascade="all, delete-orphan", order_by="CycleExercise.order",
    )


class CycleExercise(Base):
    __tablename__ = "cycle_exercises"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    cycle_workout_id: Mapped[str] = mapped_column(String, ForeignKey("cycle_workouts.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("exercises.id", ondelete="SET NULL"), nullable=True)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    workout: Mapped["CycleWorkout"] = relationship("CycleWorkout", back_populates="exercises")
    sets: Mapped[list["CycleSet"]] = relationship(
        "CycleSet", back_populates="exercise",
        cascade="all, delete-orphan", order_by="CycleSet.order",
    )


class CycleSet(Base):
    __tablename__ = "cycle_sets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    cycle_exercise_id: Mapped[str] = mapped_column(String, ForeignKey("cycle_exercises.id", ondelete="CASCADE"), nullable=False)
    percent_1rm: Mapped[float] = mapped_column(Float, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    exercise: Mapped["CycleExercise"] = relationship("CycleExercise", back_populates="sets")


class UserCycleRun(Base):
    """Tracks a user actively running a training cycle."""
    __tablename__ = "user_cycle_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cycle_id: Mapped[str] = mapped_column(String, ForeignKey("training_cycles.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    logs: Mapped[list["CycleWorkoutLog"]] = relationship(
        "CycleWorkoutLog", back_populates="run", cascade="all, delete-orphan"
    )


class CycleWorkoutLog(Base):
    """Records each workout executed within a cycle run."""
    __tablename__ = "cycle_workout_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("user_cycle_runs.id", ondelete="CASCADE"), nullable=False)
    cycle_workout_id: Mapped[str] = mapped_column(String, ForeignKey("cycle_workouts.id", ondelete="CASCADE"), nullable=False)
    workout_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    run: Mapped["UserCycleRun"] = relationship("UserCycleRun", back_populates="logs")


# ── Planned workouts ─────────────────────────────────────────────────────────

class PlannedWorkout(Base):
    __tablename__ = "planned_workouts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="Силовая")
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
    completed_workout_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exercises: Mapped[list["PlannedExercise"]] = relationship(
        "PlannedExercise",
        back_populates="planned_workout",
        cascade="all, delete-orphan",
        order_by="PlannedExercise.order",
    )


class PlannedExercise(Base):
    __tablename__ = "planned_exercises"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    planned_workout_id: Mapped[str] = mapped_column(
        String, ForeignKey("planned_workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(String, nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    planned_workout: Mapped["PlannedWorkout"] = relationship("PlannedWorkout", back_populates="exercises")
    sets: Mapped[list["PlannedSet"]] = relationship(
        "PlannedSet",
        back_populates="planned_exercise",
        cascade="all, delete-orphan",
        order_by="PlannedSet.order",
    )


class PlannedSet(Base):
    __tablename__ = "planned_sets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    planned_exercise_id: Mapped[str] = mapped_column(
        String, ForeignKey("planned_exercises.id", ondelete="CASCADE"), nullable=False
    )
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[int] = mapped_column(Integer, default=0)

    planned_exercise: Mapped["PlannedExercise"] = relationship("PlannedExercise", back_populates="sets")


class UserAchievement(Base):
    """Tracks which achievements a user has unlocked."""
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[str] = mapped_column(String(100), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserMax(Base):
    """User's manually entered 1RM values used for cycle % calculations."""
    __tablename__ = "user_maxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[date] = mapped_column(Date, default=date.today)

    user: Mapped["User"] = relationship("User", back_populates="maxes")
