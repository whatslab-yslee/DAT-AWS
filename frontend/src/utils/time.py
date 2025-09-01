from datetime import date, datetime, timedelta, timezone


KST = timezone(timedelta(hours=9))


def get_datetime_now(timezone: timezone = KST) -> datetime:
    return datetime.now(timezone)


def get_date_now(timezone: timezone = KST) -> date:
    return get_datetime_now(timezone).date()


def get_timestamp_now(timezone: timezone = KST) -> int:
    return int(get_datetime_now(timezone).timestamp())


def get_datetime_now_plus_timedelta(timedelta: timedelta, timezone: timezone = KST) -> datetime:
    return get_datetime_now(timezone) + timedelta


def get_date_now_plus_timedelta(timedelta: timedelta, timezone: timezone = KST) -> date:
    return get_datetime_now_plus_timedelta(timedelta, timezone).date()


def get_timestamp_now_plus_timedelta(timedelta: timedelta, timezone: timezone = KST) -> int:
    return int(get_datetime_now_plus_timedelta(timedelta, timezone).timestamp())


def get_datetime_now_minus_timedelta(timedelta: timedelta, timezone: timezone = KST) -> datetime:
    return get_datetime_now(timezone) - timedelta


def get_date_now_minus_timedelta(timedelta: timedelta, timezone: timezone = KST) -> date:
    return get_datetime_now_minus_timedelta(timedelta, timezone).date()


def get_timestamp_now_minus_timedelta(timedelta: timedelta, timezone: timezone = KST) -> int:
    return int(get_datetime_now_minus_timedelta(timedelta, timezone).timestamp())


def get_datetime_from_timestamp(timestamp: int, timezone: timezone = KST) -> datetime:
    return datetime.fromtimestamp(timestamp, timezone)


def get_date_from_timestamp(timestamp: int, timezone: timezone = KST) -> date:
    return get_datetime_from_timestamp(timestamp, timezone).date()


def get_total_seconds_between_datetimes(start_datetime: datetime, end_datetime: datetime, timezone: timezone = KST) -> int:
    return int((end_datetime - start_datetime).total_seconds())
