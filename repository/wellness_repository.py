from datetime import date, datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import WellnessDaily


WELLNESS_FIELDS = {
    "sleep_seconds": "sleepSecs",
    "deep_sleep_seconds": "DeepSleep",
    "rem_sleep_seconds": "REMSleep",
    "light_sleep_seconds": "LightSleep",
    "sleep_score": "sleepScore",
    "avg_sleeping_hr": "avgSleepingHR",
    "hrv_rmssd": "hrv",
    "hrv_sdnn": "hrvSDNN",
    "resting_hr": "restingHR",
    "spo2_avg": "spO2",
    "respiration_rate": "respiration",
    "vo2_max": "vo2max",
    "readiness_score": "readiness",
    "baevsky_stress_index": "baevskySI",
    "ctl": "ctl",
    "atl": "atl",
    "ramp_rate": "rampRate",
    "ctl_load": "ctlLoad",
    "atl_load": "atlLoad",
    "steps": "steps",
    "floors_climbed": "floorsClimbed",
    "active_energy": "ActiveEnergy",
    "weight_kg": "weight",
    "body_fat_percent": "bodyFat",
    "abdomen_cm": "abdomen",
    "systolic_bp": "systolic",
    "diastolic_bp": "diastolic",
    "blood_glucose": "bloodGlucose",
    "lactate": "lactate",
    "kcal_consumed": "kcalConsumed",
    "carbohydrates_g": "carbohydrates",
    "protein_g": "protein",
    "fat_total_g": "fatTotal",
    "hydration": "hydration",
    "hydration_volume": "hydrationVolume",
    "sleep_quality": "sleepQuality",
    "mood": "mood",
    "stress": "stress",
    "fatigue": "fatigue",
    "soreness": "soreness",
    "motivation": "motivation",
    "injury": "injury",
    "comments": "comments",
    "menstrual_phase": "menstrualPhase",
    "menstrual_phase_predicted": "menstrualPhasePredicted",
    "locked": "locked",
    "sport_info": "sportInfo",
    "temp_weight": "tempWeight",
    "temp_resting_hr": "tempRestingHR",
}


class WellnessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_many(self, records: list[dict[str, Any]]) -> int:
        rows_by_date = {}
        for record in records:
            record_date = date.fromisoformat(record["id"])
            ctl = record.get("ctl")
            atl = record.get("atl")
            tsb = record.get("tsb")
            if tsb is None and ctl is not None and atl is not None:
                tsb = ctl - atl

            source_updated = record.get("updated")
            source_updated_at = (
                datetime.fromisoformat(source_updated)
                if source_updated is not None else None
            )
            if source_updated_at is not None and source_updated_at.utcoffset() is None:
                raise ValueError("Wellness updated timestamp must include a timezone")

            rows_by_date[record_date] = {
                column: record.get(api_field)
                for column, api_field in WELLNESS_FIELDS.items()
            } | {
                "date": record_date,
                "tsb": tsb,
                "source_updated_at": source_updated_at,
                "raw_json": record,
            }

        rows = list(rows_by_date.values())
        if not rows:
            return 0

        # Keep bulk inserts below asyncpg's bind-parameter limit.
        batch_size = min(1000, 30000 // len(rows[0]))
        for offset in range(0, len(rows), batch_size):
            statement = insert(WellnessDaily).values(rows[offset:offset + batch_size])
            statement = statement.on_conflict_do_update(
                index_elements=[WellnessDaily.date],
                set_={
                    column: statement.excluded[column]
                    for column in rows[0]
                    if column != "date"
                } | {"updated_at": func.now()},
            )
            await self.session.execute(statement)

        return len(rows)
