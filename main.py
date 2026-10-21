import argparse
import asyncio
from datetime import date, timedelta

from clients.intervals_client import IntervalsClient
from clients.gemini_client import GeminiClient
from database.session import SessionFactory, engine, init_db
from services.daily_baseline_service import calculate_daily_baseline
from services.briefing_service import generate_daily_briefing
from services.sync_service import sync_wellness
from services.sync_service import sync_activities


async def main(start_date: date, end_date: date, briefing: bool = False) -> None:
    try:
        await init_db()
        wellness_count = await sync_wellness(
            start_date, end_date, IntervalsClient(), SessionFactory
        )
        print(f"Wellness sync complete: {wellness_count} days saved ({start_date} -> {end_date}).")
        await calculate_daily_baseline(end_date, SessionFactory)
        print(f"Daily baseline calculated for {end_date}.")

        activities_count = await sync_activities(
            start_date, end_date, IntervalsClient(), SessionFactory
        )
        print(f"Activities sync complete: {activities_count} activities saved ({start_date} -> {end_date}).")

        if briefing:
            async with GeminiClient() as client:
                result = await generate_daily_briefing(end_date, client, SessionFactory)
            print(result.model_dump_json(indent=2))

    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Intervals.icu wellness and activity data and save it to PostgreSQL."
    )
    parser.add_argument("--end-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--start-date", type=date.fromisoformat)
    parser.add_argument(
        "--briefing", action="store_true",
        help="Generate and save a Gemini briefing for --end-date after syncing (uses the paid API).",
    )
    args = parser.parse_args()
    start_date = args.start_date or args.end_date - timedelta(days=30)
    if start_date > args.end_date:
        parser.error("--start-date must not be after --end-date")
    asyncio.run(main(start_date, args.end_date, args.briefing))