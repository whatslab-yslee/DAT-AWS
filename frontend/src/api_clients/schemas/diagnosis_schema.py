from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel, Field


class DiagnosisType(StrEnum):
    NONE = auto()
    BALANCEBALL = auto()
    FITBOX = auto()
    TENNISBALL = auto()


class DiagnosisState(StrEnum):
    READY = auto()  # 준비
    STARTED = auto()  # 진행
    CANCELLED = auto()  # 취소
    FAILED = auto()  # 실패
    COMPLETED = auto()  # 완료


class DiagnosisCreate(BaseModel):
    """진단 세션 생성 요청"""

    patient_id: int = Field(..., description="환자 ID")
    type: str = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")


class DiagnosisCreateResponse(BaseModel):
    """진단 세션 생성 응답"""

    id: int = Field(..., description="진단 ID")
    code: str = Field(..., description="진단 코드")
    expired_at: datetime = Field(..., description="세션 만료 시간")


class DiagnosisStateResponse(BaseModel):
    id: int = Field(..., description="진단 ID")
    state: str = Field(..., description="진단 상태")


class DiagnosisLiveResponse(BaseModel):
    id: int = Field(..., description="진단 ID")
    code: str = Field(..., description="진단 코드")
    expired_at: datetime = Field(..., description="세션 만료 시간")


# 새로 추가하는 진단 기록 관련 스키마
class DiagnosisRecordListResponse(BaseModel):
    """진단 기록 목록 응답"""

    id: int = Field(..., description="진단 ID")
    type: str = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")
    filename: str = Field(..., description="결과 파일명")
    created_at: datetime = Field(..., description="진단 생성 시간")


class DiagnosisRecordResponse(BaseModel):
    """진단 기록 상세 응답"""

    patient_id: int = Field(..., description="환자 ID")
    type: str = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")
    created_at: datetime = Field(..., description="진단 생성 시간")
    filename: str = Field(..., description="결과 파일명")
    score: float = Field(..., description="결과 점수")
    time_spent: float = Field(..., description="결과 소요 시간")
    fps: float = Field(..., description="결과 프레임 수")
