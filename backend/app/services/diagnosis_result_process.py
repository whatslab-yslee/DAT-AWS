from dataclasses import dataclass
from datetime import datetime
import io
from typing import Tuple

from app.dtos.diagnosis_dto import DiagnosisTypeDTO
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


@dataclass
class DiagnosisScore:
    score: float
    time_spent: float
    fps: float


class DiagnosisResultProcessor:
    def __init__(self):
        pass

    def preprocess(self, type: DiagnosisTypeDTO, file: bytes) -> Tuple[bytes, DiagnosisScore]:
        # preprocess
        df = pd.read_csv(io.BytesIO(file))
        df = self._preprocess_time(df)
        if type == DiagnosisTypeDTO.TENNISBALL:
            df = self._preprocess_tennisball(df)
        df = self._sort_columns_alphabetically(df)

        # 점수 추출
        score = self._extract_score(df)

        # DataFrame to bytes
        preprocessed_file = df.to_csv(index=False).encode("utf-8")

        return preprocessed_file, score

    def _preprocess_time(self, df: pd.DataFrame) -> pd.DataFrame:
        # 점수 로깅은 state로만 판단, but
        df["time_in_seconds"] = df["current_time"].apply(self._convert_to_seconds)

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

    def _preprocess_tennisball(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._scale_pose(df)
        df = self._extract_position(df)
        return df

    def _scale_pose(self, df: pd.DataFrame) -> pd.DataFrame:
        scaler = MinMaxScaler()
        scaled_values = scaler.fit_transform(df[["Position_X", "Position_Y", "Position_Z"]])
        scaled_df = pd.DataFrame(scaled_values, columns=["Scaled_Position_X", "Scaled_Position_Y", "Scaled_Position_Z"])
        df[["Scaled_Position_X", "Scaled_Position_Y", "Scaled_Position_Z"]] = scaled_df
        return df

    def _extract_position(self, df: pd.DataFrame) -> pd.DataFrame:
        df[["Position_X", "Position_Y", "Position_Z"]] = df["Position"].str.extract(r"\(([^,]+), ([^,]+), ([^,]+)\)")
        df["Position_X"] = df["Position_X"].astype(float)
        df["Position_Y"] = df["Position_Y"].astype(float)
        df["Position_Z"] = df["Position_Z"].astype(float)
        df = df.drop(["Position"], axis=1)
        return df

    def _extract_score(self, df: pd.DataFrame) -> DiagnosisScore:
        score = self._score_report(df)
        time_spent = self._time_report(df)
        fps = df.shape[0] / time_spent

        return DiagnosisScore(
            score=float(score),
            time_spent=float(time_spent),
            fps=float(fps),
        )

    def _convert_to_seconds(self, datetime_str: str) -> float:
        # 문자열을 datetime 객체로 변환
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")

        # 기준 날짜 및 시간 (예: 1970-01-01 00:00:00.0)
        epoch = datetime(1970, 1, 1)

        # 두 datetime 객체의 차이를 계산하고, 총 초 단위로 변환
        total_seconds = (dt - epoch).total_seconds()

        return total_seconds

    def _score_report(self, df: pd.DataFrame) -> float:
        return df.iloc[-1]["Score"]

    def _time_report(self, df: pd.DataFrame) -> float:
        time_spent = self._convert_to_seconds(df.iloc[-1]["current_time"]) - self._convert_to_seconds(df.iloc[0]["current_time"])
        return time_spent

    def _sort_columns_alphabetically(self, df: pd.DataFrame) -> pd.DataFrame:
        sorted_columns = sorted(df.columns)
        df = df[sorted_columns]
        return df
