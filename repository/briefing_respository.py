from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AIBriefing, Activity, DailyBaseline, WellnessDaily
from dto.ai_dto import DailyAiBriefingDto


class BriefingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_context(self, target_date: date) -> tuple[dict, dict, list[dict]]:
        baseline = await self.session.scalar(
            select(DailyBaseline).where(DailyBaseline.date == target_date)
        )
        wellness = await self.session.scalar(
            select(WellnessDaily).where(WellnessDaily.date == target_date)
        )
        if baseline is None or wellness is None:
            raise ValueError(f"Wellness data and a calculated baseline are required for {target_date}")
        activities = await self.session.scalars(
            select(Activity)
            .where(Activity.date.between(target_date - timedelta(days=13), target_date))
            .order_by(Activity.date, Activity.start_time, Activity.id)
        )
        return (
            _record_data(baseline),
            _record_data(wellness),
            [_record_data(activity) for activity in activities],
        )

    async def upsert_briefing(self, dto: DailyAiBriefingDto) -> AIBriefing:
        raw_dict = dto.raw_ai_response if dto.raw_ai_response is not None else dto.model_dump(
            mode="json", exclude={"raw_ai_response", "created_at"}
        )

        stmt = insert(AIBriefing).values(
            date=dto.date,
            readiness_score=dto.readiness_score,
            recovery_status=dto.recovery_status,
            rec_workout_type=dto.rec_workout_type,
            rec_workout_intensity=dto.rec_workout_intensity,
            rec_workout_duration_min=dto.rec_workout_duration_min,
            key_insight=dto.key_insights,  # DTO key_insights -> DB key_insight
            raw_ai_response=raw_dict,
        )

        # ON CONFLICT (date) DO UPDATE
        stmt = stmt.on_conflict_do_update(
            index_elements=[AIBriefing.date],
            set_={
                "readiness_score": stmt.excluded.readiness_score,
                "recovery_status": stmt.excluded.recovery_status,
                "rec_workout_type": stmt.excluded.rec_workout_type,
                "rec_workout_intensity": stmt.excluded.rec_workout_intensity,
                "rec_workout_duration_min": stmt.excluded.rec_workout_duration_min,
                "key_insight": stmt.excluded.key_insight,
                "raw_ai_response": stmt.excluded.raw_ai_response,
            },
        )

        result = await self.session.execute(
            stmt.returning(AIBriefing).execution_options(populate_existing=True)
        )
        return result.scalar_one()


def _record_data(record: DailyBaseline | WellnessDaily | Activity) -> dict[str, Any]:
    return {
        column.key: getattr(record, column.key)
        for column in record.__table__.columns
        if column.key not in {"raw_json", "created_at", "updated_at"}
    }