from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from clients.intervals_client import IntervalsClient
from repository.wellness_repository import WellnessRepository
from repository.activity_repository import ActivityRepository


async def sync_wellness(
        start_date: date,
        end_date: date,
        client: IntervalsClient,
        session_factory: async_sessionmaker[AsyncSession], ) -> int:
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    wellness_records = await client.get_wellness(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )

    async with session_factory.begin() as session:
        return await WellnessRepository(session).upsert_many(wellness_records)


async def sync_activities(
        start_date: date,
        end_date: date,
        client: IntervalsClient,
        session_factory: async_sessionmaker[AsyncSession], ) -> int:
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    activity_records = await client.get_activities(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )
    async with session_factory.begin() as session:
        return await ActivityRepository(session).upsert_many(activity_records)
