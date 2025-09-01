from datetime import datetime
import re

from app.dtos.user_dto import UserRoleDTO
from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    login_id: str = Field(..., min_length=3, max_length=20, description="사용자 로그인 ID")


class UserCreate(UserBase):
    """
    User creation schema with custom password validation.
    """

    password: str = Field(..., min_length=8, description="비밀번호는 8자리 이상이어야 하며, 영문자와 숫자를 각각 최소 1자 이상 포함해야 합니다.")
    name: str = Field(..., description="사용자 이름", json_schema_extra={"example": "홍길동"})
    role: UserRoleDTO = Field(..., description="사용자 역할", json_schema_extra={"example": UserRoleDTO.DOCTOR})
    admin_code: str = Field(..., description="관리자 코드", json_schema_extra={"example": "1234"})

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validates that the password contains at least one letter and one number.
        Pydantic's `min_length=8` is checked automatically before this validator.
        """
        # 1. Check for at least one letter
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("비밀번호는 영문자를 최소 1자 이상 포함해야 합니다.")

        # 2. Check for at least one number
        if not re.search(r"\d", v):
            raise ValueError("비밀번호는 숫자를 최소 1자 이상 포함해야 합니다.")

        return v


class UserLogin(UserBase):
    password: str = Field(..., description="사용자 비밀번호")


class UserResponse(UserBase):
    id: int = Field(..., description="사용자 ID")
    name: str = Field(..., description="사용자 이름")
    role: UserRoleDTO = Field(..., description="사용자 역할")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="리프레시 토큰")
