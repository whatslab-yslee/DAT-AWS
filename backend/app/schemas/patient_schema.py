from typing import Optional

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """환자 생성 스키마"""

    code: Optional[str] = Field(None, description="환자 코드 (입력하지 않으면 자동 생성)")
    name: str = Field(..., description="환자 이름", json_schema_extra={"example": "홍길동"})


class PatientUpdate(BaseModel):
    """환자 업데이트 스키마"""

    name: Optional[str] = Field(None, description="환자 이름")


class PatientResponse(BaseModel):
    """환자 응답 스키마"""

    id: int
    code: str
    name: str
    created_at: str
    updated_at: str
