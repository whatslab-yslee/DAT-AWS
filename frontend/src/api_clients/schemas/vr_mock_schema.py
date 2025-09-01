from enum import StrEnum, auto

from pydantic import BaseModel, Field


class DiagnosisType(StrEnum):
    NONE = auto()
    BALANCEBALL = auto()
    FITBOX = auto()
    TENNISBALL = auto()


class DiagnosisJoin(BaseModel):
    code: str = Field(..., description="진단 코드")


class DiagnosisJoinResponse(BaseModel):
    id: int = Field(..., description="진단 ID")
    type: str = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")


class DiagnosisUploadRequest(BaseModel):
    id: int = Field(..., description="진단 ID")


# TODO: StrEnum 사용에 따른 코드 수정 필요 (Type.NONE.value 대신 Type.NONE 사용 등)
