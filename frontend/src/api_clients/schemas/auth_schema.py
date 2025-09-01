"""
인증 관련 스키마를 정의하는 모듈입니다.
사용자 생성, 로그인, 토큰 관련 스키마를 포함합니다.
"""

from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    NONE = auto()
    DOCTOR = auto()  # 의사
    NURSE = auto()  # 간호사
    STAFF = auto()  # 직원


class UserBase(BaseModel):
    login_id: str = Field(..., description="사용자 로그인 ID")


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, description="사용자 비밀번호")
    name: str = Field(..., description="사용자 이름")
    role: str = Field(..., description="사용자 역할")


class UserLogin(UserBase):
    password: str = Field(..., description="사용자 비밀번호")


class UserResponse(UserBase):
    id: int = Field(..., description="사용자 ID")
    name: str = Field(..., description="사용자 이름")
    role: str = Field(..., description="사용자 역할")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="리프레시 토큰")
