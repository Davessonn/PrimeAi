from datetime import date, datetime
from typing import Optional, Any, Dict
from sqlalchemy import String, Integer, Numeric, Text, Date, DateTime, Double, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass

class WellnessDaily(Base):
    __tablename__ = "wellness_daily"
    __table_args__ = {"schema": "primeAi"}

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    sleep_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deep_sleep_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    rem_sleep_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    light_sleep_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    sleep_score: Mapped[Optional[float]] = mapped_column(Double)
    avg_sleeping_hr: Mapped[Optional[float]] = mapped_column(Double)
    hrv_rmssd: Mapped[Optional[float]] = mapped_column(Double)
    hrv_sdnn: Mapped[Optional[float]] = mapped_column(Double)
    resting_hr: Mapped[Optional[float]] = mapped_column(Double)
    spo2_avg: Mapped[Optional[float]] = mapped_column(Double)
    respiration_rate: Mapped[Optional[float]] = mapped_column(Double)
    vo2_max: Mapped[Optional[float]] = mapped_column(Double)
    readiness_score: Mapped[Optional[float]] = mapped_column(Double)
    baevsky_stress_index: Mapped[Optional[float]] = mapped_column(Double)
    ctl: Mapped[Optional[float]] = mapped_column(Double)
    atl: Mapped[Optional[float]] = mapped_column(Double)
    tsb: Mapped[Optional[float]] = mapped_column(Double)
    ramp_rate: Mapped[Optional[float]] = mapped_column(Double)
    ctl_load: Mapped[Optional[float]] = mapped_column(Double)
    atl_load: Mapped[Optional[float]] = mapped_column(Double)
    steps: Mapped[Optional[int]] = mapped_column(Integer)
    floors_climbed: Mapped[Optional[int]] = mapped_column(Integer)
    active_energy: Mapped[Optional[float]] = mapped_column(Double)
    weight_kg: Mapped[Optional[float]] = mapped_column(Double)
    body_fat_percent: Mapped[Optional[float]] = mapped_column(Double)
    abdomen_cm: Mapped[Optional[float]] = mapped_column(Double)
    systolic_bp: Mapped[Optional[float]] = mapped_column(Double)
    diastolic_bp: Mapped[Optional[float]] = mapped_column(Double)
    blood_glucose: Mapped[Optional[float]] = mapped_column(Double)
    lactate: Mapped[Optional[float]] = mapped_column(Double)
    kcal_consumed: Mapped[Optional[float]] = mapped_column(Double)
    carbohydrates_g: Mapped[Optional[float]] = mapped_column(Double)
    protein_g: Mapped[Optional[float]] = mapped_column(Double)
    fat_total_g: Mapped[Optional[float]] = mapped_column(Double)
    hydration: Mapped[Optional[float]] = mapped_column(Double)
    hydration_volume: Mapped[Optional[float]] = mapped_column(Double)
    sleep_quality: Mapped[Optional[float]] = mapped_column(Double)
    mood: Mapped[Optional[float]] = mapped_column(Double)
    stress: Mapped[Optional[float]] = mapped_column(Double)
    fatigue: Mapped[Optional[float]] = mapped_column(Double)
    soreness: Mapped[Optional[float]] = mapped_column(Double)
    motivation: Mapped[Optional[float]] = mapped_column(Double)
    injury: Mapped[Optional[float]] = mapped_column(Double)
    comments: Mapped[Optional[str]] = mapped_column(Text)
    menstrual_phase: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    menstrual_phase_predicted: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    locked: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    sport_info: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSONB(none_as_null=True))
    temp_weight: Mapped[Optional[bool]] = mapped_column(Boolean)
    temp_resting_hr: Mapped[Optional[bool]] = mapped_column(Boolean)
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    hrv_z_score: Mapped[Optional[float]] = mapped_column(Double)
    sleep_debt_hours: Mapped[Optional[float]] = mapped_column(Double)
    analytics_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    raw_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tss: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    distance_meters: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    avg_hr: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_hr: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rpe: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class AIBriefing(Base):
    __tablename__ = "ai_briefings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    readiness_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recovery_status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rec_workout_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rec_workout_intensity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rec_workout_duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    key_insight: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_ai_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UserNote(Base):
    __tablename__ = "user_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
