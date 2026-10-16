from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class WellnessDTO(BaseModel):
    id: str = Field(..., description="Wellness record ID")
    date: str = Field(..., description="Date of the wellness record")
    sleep_seconds: Optional[int] = Field(default=None, description="Sleep duration in seconds")
    sleep_score: Optional[int] = Field(default=None, description="Sleep score")
    deep_sleep_seconds: Optional[int] = Field(default=None, description="Deep sleep duration in seconds")
    light_sleep_seconds: Optional[int] = Field(default=None, description="Light sleep duration in seconds")
    rem_sleep_seconds: Optional[int] = Field(default=None, description="REM sleep duration in seconds")
    avg_sleeping_hr: Optional[int] = Field(default=None, description="Average sleeping heart rate in beats per minute")
    respiration_rate: Optional[float] = Field(default=None, description="Respiration rate in breaths per minute")
    steps: Optional[int] = Field(default=None, description="Number of steps taken")
    hrv: Optional[float] = Field(default=None, description="Heart rate variability (HRV)")
    vo2_max: Optional[float] = Field(default=None, description="Estimated VO2 max")
    readiness_score: Optional[int] = Field(default=None, description="Readiness score")
    baevsky_score: Optional[float] = Field(default=None, description="Baevsky stress index score")
    spO2: Optional[float] = Field(default=None, description="Blood oxygen saturation percentage")
    hrv_SDNN: Optional[float] = Field(default=None, description="Heart rate variability (SDNN)")
    restingHR: Optional[int] = Field(default=None, description="Resting heart rate in beats per minute")
    ctl: Optional[float] = Field(default=None, description="Fitness (CTL)")
    atl: Optional[float] = Field(default=None, description="Fatigue (ATL)")
    tsb: Optional[float] = Field(default=None, description="Form (TSB)")
    ramp_rate: Optional[float] = Field(default=None, description="Ramp rate")
    raw_json: Optional[Dict[str, Any]] = Field(default=None, description="Raw JSON data")


