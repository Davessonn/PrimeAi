from datetime import date, timedelta
from math import ceil, isfinite
from statistics import fmean, stdev
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from repository.daily_baseline_repository import DailyBaselineRepository


def _number(value: Any) -> Optional[float]:
    if value is None:
        return None
    number = float(value)
    return number if isfinite(number) else None


MIN_COVERAGE = 0.7


def _values(records: list[Any], field: str, days: int, target_date: date) -> list[float]:
    start_date = target_date - timedelta(days=days - 1)
    values = [
        number
        for record in records
        if start_date <= record.date <= target_date
        if (number := _number(getattr(record, field))) is not None
    ]
    return values if len(values) >= ceil(days * MIN_COVERAGE) else []


def _average(records: list[Any], field: str, days: int, target_date: date) -> Optional[float]:
    values = _values(records, field, days, target_date)
    return fmean(values) if values else None


def _zscore(value: Any, values: list[float]) -> Optional[float]:
    current = _number(value)
    if current is None or len(values) < 2:
        return None
    deviation = stdev(values)
    if deviation == 0:
        return None
    return (current - fmean(values)) / deviation


def calculate_baseline_values(target_date: date, records: list[Any]) -> dict[str, Any]:
    today = next((record for record in records if record.date == target_date), None)
    if today is None:
        raise ValueError(f"No wellness data found for {target_date}")

    values: dict[str, Any] = {"date": target_date}
    metric_windows = {
        "hrv": ("hrv_rmssd", (14, 30, 60, 90)),
        "rhr": ("resting_hr", (14, 30, 60, 90)),
        "sleep_secs": ("sleep_seconds", (14, 30)),
        "deep_sleep_secs": ("deep_sleep_seconds", (14, 30)),
        "rem_sleep_secs": ("rem_sleep_seconds", (14, 30)),
        "respiration_rate": ("respiration_rate", (14, 30)),
        "subjective_stress": ("stress", (7,)),
    }
    for prefix, (field, windows) in metric_windows.items():
        for days in windows:
            values[f"{prefix}_{days}d_avg"] = _average(
                records, field, days, target_date
            )

    for prefix, field in (("hrv", "hrv_rmssd"), ("rhr", "resting_hr")):
        window_values = _values(records, field, 30, target_date)
        mean = fmean(window_values) if window_values else None
        deviation = stdev(window_values) if len(window_values) >= 2 else None
        values[f"{prefix}_30d_std"] = deviation
        values[f"{prefix}_30d_lower"] = (
            mean - 0.75 * deviation
            if mean is not None and deviation is not None else None
        )
        values[f"{prefix}_30d_upper"] = (
            mean + 0.75 * deviation
            if mean is not None and deviation is not None else None
        )
        values[f"{prefix}_cv_30d"] = (
            deviation / mean * 100
            if mean not in (None, 0) and deviation is not None else None
        )

    for prefix, field, days in (
        ("hrv_zscore_30d", "hrv_rmssd", 30),
        ("hrv_zscore_90d", "hrv_rmssd", 90),
        ("rhr_zscore_30d", "resting_hr", 30),
        ("rhr_zscore_90d", "resting_hr", 90),
        ("respiration_zscore_30d", "respiration_rate", 30),
    ):
        values[prefix] = _zscore(
            getattr(today, field), _values(records, field, days, target_date)
        )

    load_acwr = (
        _number(today.atl) / _number(today.ctl)
        if _number(today.atl) is not None
        and _number(today.ctl) not in (None, 0) else None
    )
    ctl_ramp_rate = _number(today.ramp_rate)
    values.update({
        "ctl": _number(today.ctl),
        "atl": _number(today.atl),
        "tsb": _number(today.tsb),
        "ctl_ramp_rate": ctl_ramp_rate,
        "load_acwr": load_acwr,
        "hrv_acwr": (
            values["hrv_14d_avg"] / values["hrv_60d_avg"]
            if values["hrv_14d_avg"] is not None
            and values["hrv_60d_avg"] not in (None, 0) else None
        ),
        "is_hrv_suppressed": (
            today.hrv_rmssd < values["hrv_30d_lower"]
            if today.hrv_rmssd is not None and values["hrv_30d_lower"] is not None
            else False
        ),
        "is_rhr_elevated": (
            today.resting_hr > values["rhr_30d_upper"]
            if today.resting_hr is not None and values["rhr_30d_upper"] is not None
            else False
        ),
        "is_injury_risk_high": (
            (
                load_acwr is not None
                and load_acwr > 1.5
            )
            or (
                ctl_ramp_rate is not None
                and ctl_ramp_rate > 7.0
            )
        ),
        "composite_stress_score": None,
    })
    return values


async def calculate_daily_baseline(
    target_date: date,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, Any]:
    start_date = target_date - timedelta(days=89)
    async with session_factory.begin() as session:
        repository = DailyBaselineRepository(session)
        history = await repository.get_wellness_history(start_date, target_date)
        values = calculate_baseline_values(target_date, history)
        await repository.upsert(values)
        return values
