from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DailyBaseline, WellnessDaily


class DailyBaselineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_wellness_history(
        self, start_date: date, end_date: date
    ) -> list[WellnessDaily]:
        result = await self.session.execute(
            select(WellnessDaily)
            .where(WellnessDaily.date.between(start_date, end_date))
            .order_by(WellnessDaily.date)
        )
        return list(result.scalars().all())

    async def upsert(self, values: dict[str, Any]) -> None:
        statement = insert(DailyBaseline).values(values)
        statement = statement.on_conflict_do_update(
            index_elements=[DailyBaseline.date],
            set_={
                column: statement.excluded[column]
                for column in values
                if column != "date"
            } | {"calculated_at": func.now()},
        )
        await self.session.execute(statement)
