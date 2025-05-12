from datetime import datetime, time, timedelta
from typing import Optional

import pytz


def convert_to_eastern(dt: Optional[datetime] = None) -> datetime:
    """Convert a datetime to US Eastern time.

    Args:
        dt: datetime to convert (naive or with timezone)

    Returns:
        Datetime in US Eastern timezone
    """
    if dt is None:
        dt = datetime.now()

    eastern = pytz.timezone("US/Eastern")

    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)

    # Convert to Eastern
    return dt.astimezone(eastern)


def is_market_open(dt: Optional[datetime] = None) -> bool:
    """Check if the US stock market is open at the given time.

    Args:
        dt: Datetime to check (defaults to current time)

    Returns:
        True if market is open, False otherwise
    """
    if dt is None:
        dt = datetime.now()

    # Convert to Eastern time
    et_time = convert_to_eastern(dt)

    # Check if weekend
    if et_time.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False

    # Check standard market hours (9:30 AM to 4:00 PM ET)
    market_open = time(9, 30)
    market_close = time(16, 0)

    # Get just the time component
    current_time = et_time.time()

    # Check if within market hours
    return market_open <= current_time < market_close


def get_next_market_close_timestamp() -> float:
    """
    Get timestamp for the next market close.

    Returns:
        Unix timestamp for next market close
    """
    now = datetime.now(pytz.utc)
    et_now = convert_to_eastern(now)

    # Create datetime for today's market close (4:00 PM ET)
    eastern = pytz.timezone("US/Eastern")
    today = et_now.date()
    close_time = time(16, 0)
    close_dt = eastern.localize(datetime.combine(today, close_time))

    # If current time is past market close, move to next trading day
    if et_now >= close_dt:
        # Find next trading day (skipping weekends)
        days_to_add = 1
        if et_now.weekday() == 4:  # Friday
            days_to_add = 3  # Skip to Monday
        elif et_now.weekday() == 5:  # Saturday
            days_to_add = 2  # Skip to Monday

        import pandas as pd

        next_day = today + pd.Timedelta(days=days_to_add)
        close_dt = eastern.localize(datetime.combine(next_day, close_time))

    # Convert to timestamp
    return close_dt.timestamp()


def is_premarket_open(dt: Optional[datetime] = None) -> bool:
    """Check if the US stock premarket is open at the given time.

    Args:
        dt: Datetime to check (defaults to current time)

    Returns:
        True if premarket is open, False otherwise
    """
    if dt is None:
        dt = datetime.now()

    # Convert to Eastern time
    et_time = convert_to_eastern(dt)

    # Check if weekend
    if et_time.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False

    # Check premarket hours (4:00 AM to 9:30 AM ET)
    premarket_open = time(4, 0)
    market_open = time(9, 30)

    # Get just the time component
    current_time = et_time.time()

    # Check if within premarket hours
    return premarket_open <= current_time < market_open


def is_afterhours_open(dt: Optional[datetime] = None) -> bool:
    """Check if the US stock afterhours market is open at the given time.

    Args:
        dt: Datetime to check (defaults to current time)

    Returns:
        True if afterhours is open, False otherwise
    """
    if dt is None:
        dt = datetime.now()

    # Convert to Eastern time
    et_time = convert_to_eastern(dt)

    # Check if weekend
    if et_time.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False

    # Check afterhours (4:00 PM to 8:00 PM ET)
    market_close = time(16, 0)
    afterhours_close = time(20, 0)

    # Get just the time component
    current_time = et_time.time()

    # Check if within afterhours
    return market_close <= current_time < afterhours_close


def get_next_market_open() -> datetime:
    """Get the next market open datetime.

    Returns:
        Datetime of next market open
    """
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)

    # Start with today
    next_open_day = now.date()

    # If it's after market close or weekend, move to next trading day
    if now.weekday() >= 5 or (now.weekday() == 4 and now.time() >= time(16, 0)):
        # If Friday after close or weekend, move to Monday
        days_to_add = 7 - now.weekday() if now.weekday() >= 5 else 3
        next_open_day = (now + timedelta(days=days_to_add)).date()
    elif now.time() >= time(16, 0):
        # If after market close, move to next day
        next_open_day = (now + timedelta(days=1)).date()

    # Create datetime for next market open (9:30 AM ET)
    next_open = eastern.localize(datetime.combine(next_open_day, time(9, 30)))

    return next_open


def get_next_market_close() -> datetime:
    """Get the next market close datetime.

    Returns:
        Datetime of next market close
    """
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)

    # Start with today
    next_close_day = now.date()

    # If it's after market close or weekend, move to next trading day
    if now.weekday() >= 5 or (now.weekday() == 4 and now.time() >= time(16, 0)):
        # If Friday after close or weekend, move to Monday
        days_to_add = 7 - now.weekday() if now.weekday() >= 5 else 3
        next_close_day = (now + timedelta(days=days_to_add)).date()
    elif now.time() >= time(16, 0):
        # If after market close, move to next day
        next_close_day = (now + timedelta(days=1)).date()

    # Create datetime for next market close (4:00 PM ET)
    next_close = eastern.localize(datetime.combine(next_close_day, time(16, 0)))

    return next_close


def time_to_next_market_open() -> timedelta:
    """Get the time until the next market open.

    Returns:
        Timedelta until next market open
    """
    now = datetime.now(pytz.timezone("US/Eastern"))
    next_open = get_next_market_open()

    return next_open - now


def format_time_remaining(td: timedelta) -> str:
    """Format a timedelta as a human-readable string.

    Args:
        td: Timedelta to format

    Returns:
        Formatted string
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours}h {minutes}m {seconds}s"

