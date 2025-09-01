from datetime import datetime

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def pose_scailing(df):
    scaler = MinMaxScaler()
    scaled_values = scaler.fit_transform(df[["Position_X", "Position_Y", "Position_Z"]])
    scaled_df = pd.DataFrame(scaled_values, columns=["Scaled_Position_X", "Scaled_Position_Y", "Scaled_Position_Z"])
    df[["Scaled_Position_X", "Scaled_Position_Y", "Scaled_Position_Z"]] = scaled_df
    return df


def position_extract(df):
    df[["Position_X", "Position_Y", "Position_Z"]] = df["Position"].str.extract(r"\(([^,]+), ([^,]+), ([^,]+)\)")
    df["Position_X"] = df["Position_X"].astype(float)
    df["Position_Y"] = df["Position_Y"].astype(float)
    df["Position_Z"] = df["Position_Z"].astype(float)
    df = df.drop(["Position"], axis=1)
    return df


def milliseconds_from_timedelta(timedelta):
    """Compute the milliseconds in a timedelta as floating-point number"""
    return timedelta.total_seconds() * 1e3


def preprocessing(df):
    # 점수 로깅은 state로만 판단, but
    df["time_in_seconds"] = df["current_time"].apply(convert_to_seconds)

    df["event"] = ""
    df["spend_time"] = ""

    start_time = df["time_in_seconds"][0]

    for i in range(1, len(df)):
        if df["State"][i] < df["State"][i - 1]:
            fail_time = df["time_in_seconds"][i]
            df.loc[i, "event"] = "Fail"
            df.loc[i, "spend_time"] = f"{fail_time - start_time}ms"
            start_time = fail_time
        elif df["State"][i] > df["State"][i - 1]:
            fail_time = df["time_in_seconds"][i]
            df.loc[i, "event"] = "Success"
            df.loc[i, "spend_time"] = f"{fail_time - start_time}ms"

    start = df["time_in_seconds"][0]

    df["time (second)"] = df["time_in_seconds"] - start

    df = df.drop(columns=["time_in_seconds"])

    return df


def score_report(df):
    return df.iloc[-1]["Score"]


def time_report(df):
    time_spent = convert_to_seconds(df.iloc[-1]["current_time"]) - convert_to_seconds(df.iloc[0]["current_time"])
    return time_spent


def convert_to_seconds(datetime_str):
    # 문자열을 datetime 객체로 변환
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")

    # 기준 날짜 및 시간 (예: 1970-01-01 00:00:00.0)
    epoch = datetime(1970, 1, 1)

    # 두 datetime 객체의 차이를 계산하고, 총 초 단위로 변환
    total_seconds = (dt - epoch).total_seconds()

    return total_seconds


def sort_columns_alphabetically(df):
    sorted_columns = sorted(df.columns)
    df = df[sorted_columns]
    return df
