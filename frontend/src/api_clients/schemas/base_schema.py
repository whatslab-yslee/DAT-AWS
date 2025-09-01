"""
API 응답 관련 기본 스키마를 정의하는 모듈입니다.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """API 응답 기본 스키마"""

    success: bool = Field(..., description="API 요청 성공 여부")
    data: Optional[Any] = Field(None, description="응답 데이터")
    error: Optional[str] = Field(None, description="오류 메시지")
    details: Optional[str] = Field(None, description="오류 상세 정보")
    status_code: Optional[int] = Field(None, description="HTTP 상태 코드")


class MessageResponse(BaseModel):
    message: str = Field(..., description="응답 메시지")
