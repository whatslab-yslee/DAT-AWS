from typing import Optional

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """환자 생성 스키마"""

    name: str = Field(..., description="환자 이름")
    code: Optional[str] = Field(None, description="환자 코드")


class PatientUpdate(BaseModel):
    """환자 수정 스키마"""

    name: str = Field(..., description="환자 이름")


class PatientResponse(BaseModel):
    """환자 응답 스키마"""

    id: int = Field(..., description="환자 ID")
    code: str = Field(..., description="환자 코드")
    name: str = Field(..., description="환자 이름")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="수정 시간")
