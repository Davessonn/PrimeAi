from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Activity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_many(self, records: list[dict[str, Any]]) -> int:
        rows_by_id = {}
        for record in records:
            activity_id = record["id"]
            activity_type = record["type"]
            if not isinstance(activity_id, str) or not activity_id.strip():
                raise ValueError("Activity id must be a non-empty string")
            if not isinstance(activity_type, str) or not activity_type.strip():
                raise ValueError(f"Activity {activity_id}: type must be a non-empty string")

            start_time = datetime.fromisoformat(record["start_date"])
            if start_time.utcoffset() is None:
                raise ValueError(f"Activity {activity_id}: start_date must include a timezone")
            local_start = datetime.fromisoformat(record["start_date_local"])
            avg_watts = record.get("icu_average_watts")
            normalized_power = record.get("icu_weighted_avg_watts")

            rows_by_id[activity_id] = {
                "id": activity_id,
                "date": local_start.date(),
                "start_time": start_time,
                "type": activity_type,
                "name": record.get("name"),
                "duration_seconds": record.get("moving_time"),
                "tss": record.get("icu_training_load"),
                "distance_meters": record.get("distance"),
                "elevation_gain_meters": record.get("total_elevation_gain"),
                "avg_hr": record.get("average_heartrate"),
                "max_hr": record.get("max_heartrate"),
                "avg_watts": round(avg_watts) if avg_watts is not None else None,
                "normalized_power": (
                    round(normalized_power) if normalized_power is not None else None
                ),
                "calories": record.get("calories"),
                "rpe": record.get("icu_rpe"),
                "raw_json": record,
            }

        rows = list(rows_by_id.values())
        if not rows:
            return 0

        batch_size = min(1000, 30000 // len(rows[0]))
        for offset in range(0, len(rows), batch_size):
            statement = insert(Activity).values(rows[offset:offset + batch_size])
            statement = statement.on_conflict_do_update(
                index_elements=[Activity.id],
                set_={
                    column: statement.excluded[column]
                    for column in rows[0]
                    if column != "id"
                },
            )
            await self.session.execute(statement)

        return len(rows)
