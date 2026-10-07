from datetime import date, datetime
from typing import Optional

_Date = date  # alias to avoid field-name shadowing in Pydantic models

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

class AchievementOut(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    category: str
    unlocked: bool
    unlockedAt: Optional[datetime] = None


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
    isAdmin: bool = False


# ---------------------------------------------------------------------------
# Exercise
# ---------------------------------------------------------------------------

class ExerciseCreate(BaseModel):
    name: str
    muscleGroup: str
    secondaryMuscles: list[str] = []
    equipment: str
    description: str = ""
    isPrivate: bool = False


class ExerciseOut(BaseModel):
    id: str
    name: str
    muscleGroup: str
    secondaryMuscles: list[str]
    equipment: str
    description: str
    isCustom: bool
    status: str = "approved"


# ---------------------------------------------------------------------------
# Sets / WorkoutExercise
# ---------------------------------------------------------------------------

class SetIn(BaseModel):
    weight: float = 0.0
    reps: int = 0
    completed: bool = False
    failed: bool = False
    rpe: Optional[float] = Field(None, ge=1, le=10)


class SetOut(BaseModel):
    id: str
    weight: float
    reps: int
    completed: bool
    failed: bool = False
    rpe: Optional[float] = None


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
    birthDate: Optional[date] = None
    avatarUrl: Optional[str] = None


class ThemeUpdate(BaseModel):
    theme: str  # "light" | "dark"


class PasswordChange(BaseModel):
    currentPassword: str
    newPassword: str


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
    birthDate: Optional[date] = None
    avatarUrl: Optional[str]
    theme: str = "light"
    isAdmin: bool = False
    isCoach: bool = False
    coachBio: str = ""
    coachAccepting: bool = False
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


class CycleMainExercise(BaseModel):
    exerciseId: Optional[str] = None
    exerciseName: str


class CycleCreate(BaseModel):
    title: str
    description: str = ""
    author_name: str = ""
    is_public: bool = False
    main_exercises: list[CycleMainExercise] = []
    workouts: list[CycleWorkoutIn] = []


class CycleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author_name: Optional[str] = None
    is_public: Optional[bool] = None
    main_exercises: Optional[list[CycleMainExercise]] = None
    workouts: Optional[list[CycleWorkoutIn]] = None


class CycleListOut(BaseModel):
    id: str
    title: str
    description: str
    author_name: str
    created_by: int
    is_public: bool
    is_approved: bool = True
    created_at: datetime
    workout_count: int
    main_exercises: list[CycleMainExercise] = []


class CycleDetailOut(BaseModel):
    id: str
    title: str
    description: str
    author_name: str
    created_by: int
    is_public: bool
    is_approved: bool = True
    created_at: datetime
    main_exercises: list[CycleMainExercise] = []
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


# ---------------------------------------------------------------------------
# Planned workouts
# ---------------------------------------------------------------------------

class PlannedSetIn(BaseModel):
    weight: float = 0.0
    reps: int = 0


class PlannedSetOut(BaseModel):
    id: str
    weight: float
    reps: int


class PlannedExerciseIn(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: list[PlannedSetIn] = []


class PlannedExerciseOut(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: list[PlannedSetOut]


class PlannedWorkoutCreate(BaseModel):
    title: str
    type: str = "Силовая"
    scheduledDate: date
    notes: str = ""
    exercises: list[PlannedExerciseIn] = []
    # When laid out from a training cycle: the cycle, and one id shared by
    # every plan of that layout.
    cycleId: Optional[str] = None
    cycleScheduleId: Optional[str] = Field(None, max_length=36)


class PlannedWorkoutUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    scheduledDate: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    completedWorkoutId: Optional[str] = None
    exercises: Optional[list[PlannedExerciseIn]] = None


class PlannedWorkoutOut(BaseModel):
    id: str
    title: str
    type: str
    scheduledDate: date
    notes: str
    status: str
    completedWorkoutId: Optional[str]
    createdAt: datetime
    exercises: list[PlannedExerciseOut]
    # Set when someone other than the athlete (their coach) wrote the plan.
    createdById: Optional[int] = None
    createdByName: Optional[str] = None
    cycleId: Optional[str] = None
    cycleScheduleId: Optional[str] = None
    cycleTitle: Optional[str] = None
    cycleMainExercises: list[CycleMainExercise] = []


# ---------------------------------------------------------------------------
# Workout templates
# ---------------------------------------------------------------------------

class TemplateSetIn(BaseModel):
    weight: float = 0.0
    reps: int = 0


class TemplateSetOut(BaseModel):
    id: str
    weight: float
    reps: int


class TemplateExerciseIn(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: list[TemplateSetIn] = []


class TemplateExerciseOut(BaseModel):
    exerciseId: str
    exerciseName: str
    sets: list[TemplateSetOut]


class WorkoutTemplateCreate(BaseModel):
    title: str
    type: str = "Силовая"
    exercises: list[TemplateExerciseIn] = []


class WorkoutTemplateUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    exercises: Optional[list[TemplateExerciseIn]] = None


class WorkoutTemplateOut(BaseModel):
    id: str
    title: str
    type: str
    createdAt: datetime
    exercises: list[TemplateExerciseOut]


# ---------------------------------------------------------------------------
# Social
# ---------------------------------------------------------------------------

class CoachLinkBrief(BaseModel):
    """The open (pending/active) coaching link between the viewer and a profile."""
    id: str
    status: str
    myRole: str            # coach | athlete — the viewer's side of the link
    initiatedByMe: bool


class PublicPersonOut(BaseModel):
    id: int
    name: str
    avatarUrl: Optional[str] = None


class UserPublicOut(BaseModel):
    id: int
    name: str
    avatarUrl: Optional[str] = None
    age: Optional[int] = None
    followersCount: int
    followingCount: int
    workoutsCount: int
    isFollowing: bool
    followsMe: bool = False
    isCoach: bool = False
    coachBio: str = ""
    coachAccepting: bool = False
    coachLink: Optional[CoachLinkBrief] = None
    coaches: list[PublicPersonOut] = []          # who coaches this user (active links)
    athletesCount: Optional[int] = None          # for coaches only
    # Only for the user themself and their active coach allowed to see private data.
    currentWeight: Optional[WeightEntryOut] = None


class ActivityDayOut(BaseModel):
    date: str
    count: int


class PublicMaxOut(BaseModel):
    exerciseName: str
    weightKg: float


class PublicGoalOut(BaseModel):
    text: str
    targetDate: Optional[_Date] = None


class PublicAchievementOut(BaseModel):
    id: str
    title: str
    icon: str
    category: str
    unlockedAt: datetime


class UserSearchOut(BaseModel):
    id: int
    name: str
    avatarUrl: Optional[str] = None
    isFollowing: bool


class FollowStatusOut(BaseModel):
    isFollowing: bool
    followersCount: int


class FeedWorkoutOut(BaseModel):
    id: str
    date: _Date
    type: str
    title: str
    durationMinutes: int
    notes: str
    createdAt: datetime
    exercises: list[WorkoutExerciseOut]
    userId: int
    userName: str
    userAvatarUrl: Optional[str] = None
    likesCount: int = 0
    commentsCount: int = 0
    isLiked: bool = False


class LikeStatusOut(BaseModel):
    isLiked: bool
    likesCount: int


class WorkoutMetaOut(BaseModel):
    workoutId: str
    likesCount: int
    commentsCount: int
    isLiked: bool


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationOut(BaseModel):
    id: str
    type: str
    actorId: int
    actorName: str
    workoutId: Optional[str] = None
    workoutTitle: Optional[str] = None
    commentText: Optional[str] = None
    coachLinkId: Optional[str] = None
    coachLinkStatus: Optional[str] = None
    plannedWorkoutId: Optional[str] = None
    isRead: bool
    createdAt: datetime


class NotificationsPageOut(BaseModel):
    items: list[NotificationOut]
    hasMore: bool
    total: int


class UnreadCountOut(BaseModel):
    count: int


class WorkoutCommentIn(BaseModel):
    text: str


class WorkoutCommentOut(BaseModel):
    id: str
    userId: int
    userName: str
    text: str
    createdAt: datetime
    isOwn: bool = False


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

class AdminUserOut(BaseModel):
    id: int
    email: Optional[str] = None
    name: str
    isAdmin: bool


class AdminUserUpdate(BaseModel):
    isAdmin: bool


class AdminPasswordReset(BaseModel):
    newPassword: str


class AdminExerciseOut(BaseModel):
    id: str
    name: str
    muscleGroup: str
    secondaryMuscles: list[str]
    equipment: str
    description: str
    status: str
    submittedByName: Optional[str] = None
    submittedByEmail: Optional[str] = None


class AdminExerciseCreate(BaseModel):
    name: str
    muscleGroup: str
    secondaryMuscles: list[str] = []
    equipment: str
    description: str = ""


class AdminExerciseUpdate(BaseModel):
    name: str


class AdminCycleOut(BaseModel):
    id: str
    title: str
    description: str
    authorName: str
    isPublic: bool
    isApproved: bool
    workoutCount: int
    createdAt: datetime
    submittedByName: Optional[str] = None
    submittedByEmail: Optional[str] = None


class DailyCountOut(BaseModel):
    date: str
    count: int


class TopUserOut(BaseModel):
    id: int
    name: str
    workoutCount: int


class AdminStatsOut(BaseModel):
    totalUsers: int
    newUsersLast7Days: int
    totalWorkouts: int
    workoutsLast7Days: int
    totalExercises: int
    customExercises: int
    pendingExercises: int
    totalCycles: int
    publicCycles: int
    pendingCycles: int
    dailyWorkouts: list[DailyCountOut]
    topUsers: list[TopUserOut]


# ---------------------------------------------------------------------------
# Coaching
# ---------------------------------------------------------------------------

class CoachSettingsUpdate(BaseModel):
    isCoach: Optional[bool] = None
    coachBio: Optional[str] = Field(None, max_length=2000)
    coachAccepting: Optional[bool] = None


class CoachInviteIn(BaseModel):
    athleteId: int
    message: str = Field("", max_length=500)


class CoachRequestIn(BaseModel):
    coachId: int
    message: str = Field("", max_length=500)


class CoachLinkPermissionsUpdate(BaseModel):
    canSeePrivate: Optional[bool] = None
    canEditPlan: Optional[bool] = None


class CoachLinkOut(BaseModel):
    id: str
    coachId: int
    coachName: str
    coachAvatarUrl: Optional[str] = None
    athleteId: int
    athleteName: str
    athleteAvatarUrl: Optional[str] = None
    status: str
    initiatedBy: str
    canSeePrivate: bool
    canEditPlan: bool
    message: str = ""
    createdAt: datetime
    respondedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None


class AthleteSummaryOut(BaseModel):
    linkId: str
    id: int
    name: str
    avatarUrl: Optional[str] = None
    canSeePrivate: bool
    canEditPlan: bool
    since: Optional[datetime] = None
    lastWorkoutDate: Optional[date] = None
    weekPlanned: int = 0
    weekCompleted: int = 0
