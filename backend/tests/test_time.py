from datetime import date, datetime, timedelta, timezone

from app.utils.time import (
    KST,
    get_date_from_timestamp,
    get_date_now,
    get_date_now_minus_timedelta,
    get_date_now_plus_timedelta,
    get_datetime_from_timestamp,
    get_datetime_now,
    get_datetime_now_minus_timedelta,
    get_datetime_now_plus_timedelta,
    get_timestamp_now,
    get_timestamp_now_minus_timedelta,
    get_timestamp_now_plus_timedelta,
)


def test_get_datetime_now():
    now = get_datetime_now()
    assert isinstance(now, datetime)
    assert now.tzinfo == KST


def test_get_date_now():
    today = get_date_now()
    assert isinstance(today, date)
    assert today == get_datetime_now().date()


def test_get_timestamp_now():
    timestamp = get_timestamp_now()
    assert isinstance(timestamp, int)
    assert timestamp == int(get_datetime_now().timestamp())


def test_get_datetime_now_plus_timedelta():
    delta = timedelta(days=1)
    future = get_datetime_now_plus_timedelta(delta)
    assert isinstance(future, datetime)
    assert future.tzinfo == KST
    assert future > get_datetime_now()


def test_get_date_now_plus_timedelta():
    delta = timedelta(days=1)
    future_date = get_date_now_plus_timedelta(delta)
    assert isinstance(future_date, date)
    assert future_date > get_date_now()


def test_get_timestamp_now_plus_timedelta():
    delta = timedelta(days=1)
    future_timestamp = get_timestamp_now_plus_timedelta(delta)
    assert isinstance(future_timestamp, int)
    assert future_timestamp > get_timestamp_now()


def test_get_datetime_now_minus_timedelta():
    delta = timedelta(days=1)
    past = get_datetime_now_minus_timedelta(delta)
    assert isinstance(past, datetime)
    assert past.tzinfo == KST
    assert past < get_datetime_now()


def test_get_date_now_minus_timedelta():
    delta = timedelta(days=1)
    past_date = get_date_now_minus_timedelta(delta)
    assert isinstance(past_date, date)
    assert past_date < get_date_now()


def test_get_timestamp_now_minus_timedelta():
    delta = timedelta(days=1)
    past_timestamp = get_timestamp_now_minus_timedelta(delta)
    assert isinstance(past_timestamp, int)
    assert past_timestamp < get_timestamp_now()


def test_get_datetime_from_timestamp():
    current_timestamp = get_timestamp_now()
    dt = get_datetime_from_timestamp(current_timestamp)
    assert isinstance(dt, datetime)
    assert dt.tzinfo == KST
    assert int(dt.timestamp()) == current_timestamp


def test_get_date_from_timestamp():
    current_timestamp = get_timestamp_now()
    d = get_date_from_timestamp(current_timestamp)
    assert isinstance(d, date)
    assert d == get_datetime_from_timestamp(current_timestamp).date()


def test_custom_timezone():
    utc = timezone.utc
    now_utc = get_datetime_now(utc)
    assert now_utc.tzinfo == utc
    assert now_utc != get_datetime_now(KST)
