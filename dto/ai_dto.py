from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class GeminiBriefingResponseDto(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    readiness_score: int = Field(
        strict=True,
        ge=0,
        le=100,
        description="Daily readiness score from 0 (exhausted) to 100 (prime condition)",
    )
    recovery_status: str = Field(
        min_length=1,
        description="Short description of recovery status (e.g. 'Fully Recovered', 'Moderate Fatigue')"
    )
    rec_workout_type: str = Field(
        min_length=1,
        description="Recommended workout type (e.g. 'Zone 2 Endurance', 'Rest Day', 'VO2Max Intervals')"
    )
    rec_workout_intensity: str = Field(
        min_length=1,
        description="Recommended workout intensity (e.g. 'Low', 'Moderate', 'High')"
    )
    rec_workout_duration_min: int = Field(
        strict=True, ge=0, le=1440,
        description="Recommended workout duration in minutes (e.g. 0, 45, 90)"
    )
    key_insights: str = Field(
        min_length=1,
        description="Concise analytical insight explaining the reasoning based on HRV, RHR, Z-scores and training load"
    )


class DailyAiBriefingDto(GeminiBriefingResponseDto):
    """A teljes DTO, amit a Repository-nak és a Servicenek adunk át."""

    date: date
    raw_ai_response: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
