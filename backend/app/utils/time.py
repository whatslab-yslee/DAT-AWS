from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")


def get_datetime_now(target_timezone: ZoneInfo = KST) -> datetime:
    return datetime.now(target_timezone)


def get_date_now(target_timezone: ZoneInfo = KST) -> date:
    return get_datetime_now(target_timezone).date()


def get_timestamp_now(target_timezone: ZoneInfo = KST) -> int:
    return int(get_datetime_now(target_timezone).timestamp())


def get_datetime_now_plus_timedelta(delta: timedelta, target_timezone: ZoneInfo = KST) -> datetime:
    return get_datetime_now(target_timezone) + delta


def get_date_now_plus_timedelta(delta: timedelta, target_timezone: ZoneInfo = KST) -> date:
    return get_datetime_now_plus_timedelta(delta, target_timezone).date()


def get_timestamp_now_plus_timedelta(delta: timedelta, target_timezone: ZoneInfo = KST) -> int:
    return int(get_datetime_now_plus_timedelta(delta, target_timezone).timestamp())


def get_datetime_now_minus_timedelta(delta: timedelta, target_timezone: ZoneInfo = KST) -> datetime:
    return get_datetime_now(target_timezone) - delta


def get_date_now_minus_timedelta(delta: timedelta, target_timezone: ZoneInfo = KST) -> date:
    return get_datetime_now_minus_timedelta(delta, target_timezone).date()


def get_timestamp_now_minus_timedelta(delta: timedelta, target_timezone: ZoneInfo = KST) -> int:
    return int(get_datetime_now_minus_timedelta(delta, target_timezone).timestamp())


def get_datetime_from_timestamp(timestamp: int, target_timezone: ZoneInfo = KST) -> datetime:
    return datetime.fromtimestamp(timestamp, target_timezone)


def get_date_from_timestamp(timestamp: int, target_timezone: ZoneInfo = KST) -> date:
    return get_datetime_from_timestamp(timestamp, target_timezone).date()


def convert_kst_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)

    return dt.astimezone(timezone.utc)


def convert_utc_to_kst(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.tzinfo != timezone.utc:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(KST)
