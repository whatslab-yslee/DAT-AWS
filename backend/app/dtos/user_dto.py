from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from app.utils import convert_utc_to_kst


class UserRoleDTO(str, Enum):
    NONE = "NONE"
    DOCTOR = "DOCTOR"  # 의사
    NURSE = "NURSE"  # 간호사
    STAFF = "STAFF"  # 직원


@dataclass
class UserDTO:
    id: int
    login_id: str
    name: str
    role: UserRoleDTO
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    @classmethod
    def from_model(cls, user: Any) -> "UserDTO":
        return cls(
            id=user.id,
            login_id=user.login_id,
            name=user.name,
            role=UserRoleDTO(user.role.value),
            created_at=convert_utc_to_kst(user.created_at),
            updated_at=convert_utc_to_kst(user.updated_at),
            is_deleted=user.is_deleted,
        )


@dataclass
class UserRegistrationInputDTO:
    login_id: str
    password: str
    name: str
    role: UserRoleDTO
    admin_code: str


@dataclass
class UserLoginDTO:
    login_id: str
    password: str


@dataclass
class TokenPairDTO:
    access_token: str
    refresh_token: str
