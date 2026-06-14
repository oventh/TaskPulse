"""Time utility — Beijing time (Asia/Shanghai, UTC+8)."""

from datetime import datetime, timezone, timedelta, tzinfo

# Beijing timezone (UTC+8, no DST)
_BJ_TZ = timezone(timedelta(hours=8))


def now() -> datetime:
    """Return current time in UTC (naive, for DB storage)."""
    return datetime.utcnow()


def now_bj() -> datetime:
    """Return current time as Beijing time (aware)."""
    return datetime.now(_BJ_TZ)


def fmt_bj(dt: datetime | None) -> str:
    """Format a naive datetime (assumed UTC) as Beijing time string.
    
    Returns e.g. '2026-06-15 10:30:00'
    """
    if dt is None:
        return "—"
    # Assume naive dt is UTC
    utc_dt = dt.replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(_BJ_TZ)
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")
