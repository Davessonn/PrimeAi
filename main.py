import argparse
import asyncio
from datetime import date, timedelta

from clients.intervals_client import IntervalsClient
from database.session import SessionFactory, engine, init_db
from services.sync_service import sync_wellness
from services.sync_service import sync_activities


async def main(start_date: date, end_date: date) -> None:
    try:
        await init_db()
        wellness_count = await sync_wellness(
            start_date, end_date, IntervalsClient(), SessionFactory
        )
        print(f"Wellness sync complete: {wellness_count} days saved ({start_date} -> {end_date}).")

        activities_count = await sync_activities(
            start_date, end_date, IntervalsClient(), SessionFactory
        )
        print(f"Activities sync complete: {activities_count} activities saved ({start_date} -> {end_date}).")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Intervals.icu wellness and activity data and save it to PostgreSQL."
    )
    parser.add_argument("--end-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--start-date", type=date.fromisoformat)
    args = parser.parse_args()
    start_date = date(2026, 3, 8);"""args.start_date or args.end_date - timedelta(days=30)"""
    if start_date > args.end_date:
        parser.error("--start-date must not be after --end-date")
    asyncio.run(main(start_date, args.end_date))