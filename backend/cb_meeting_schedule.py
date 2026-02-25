"""Central bank meeting schedules for countdown and policy tracker.

FOMC dates from https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
Updated annually when Fed publishes new calendar.
"""

from datetime import date
from typing import List, Optional, Tuple

# FOMC meeting dates: (date, has_sep) — has_sep = Summary of Economic Projections (dot plot)
# Policy decision is announced on the last day of the meeting.
_FOMC_MEETINGS: List[Tuple[date, bool]] = [
    # 2025
    (date(2025, 1, 29), False),
    (date(2025, 3, 19), True),   # SEP
    (date(2025, 5, 7), False),
    (date(2025, 6, 18), True),   # SEP
    (date(2025, 7, 30), False),
    (date(2025, 9, 17), True),   # SEP
    (date(2025, 10, 29), False),
    (date(2025, 12, 10), True),  # SEP
    # 2026
    (date(2026, 1, 28), False),
    (date(2026, 3, 18), True),   # SEP
    (date(2026, 4, 29), False),
    (date(2026, 6, 17), True),   # SEP
    (date(2026, 7, 29), False),
    (date(2026, 9, 16), True),   # SEP
    (date(2026, 10, 28), False),
    (date(2026, 12, 9), True),   # SEP
    # 2027 (typical pattern; update when Fed publishes)
    (date(2027, 1, 27), False),
    (date(2027, 3, 17), True),
    (date(2027, 5, 8), False),
    (date(2027, 6, 16), True),
    (date(2027, 7, 28), False),
    (date(2027, 9, 15), True),
    (date(2027, 10, 27), False),
    (date(2027, 12, 8), True),
]


def get_next_fomc_meeting(as_of: Optional[date] = None) -> Optional[Tuple[date, bool]]:
    """Return (meeting_date, has_sep) for the next FOMC meeting, or None if all past."""
    today = as_of or date.today()
    for meeting_date, has_sep in _FOMC_MEETINGS:
        if meeting_date >= today:
            return (meeting_date, has_sep)
    return None


def get_upcoming_fomc_meetings(as_of: Optional[date] = None, limit: int = 4) -> List[dict]:
    """Return list of upcoming FOMC meetings with countdown."""
    today = as_of or date.today()
    result = []
    for meeting_date, has_sep in _FOMC_MEETINGS:
        if meeting_date >= today and len(result) < limit:
            delta = (meeting_date - today).days
            result.append({
                "date": meeting_date.isoformat(),
                "days_until": delta,
                "has_sep": has_sep,
                "label": f"{meeting_date.strftime('%b %d')}{' (SEP)' if has_sep else ''}",
            })
    return result


def days_until_next_fomc(as_of: Optional[date] = None) -> Optional[int]:
    """Days until next FOMC meeting."""
    next_ = get_next_fomc_meeting(as_of)
    if next_ is None:
        return None
    today = as_of or date.today()
    return (next_[0] - today).days
