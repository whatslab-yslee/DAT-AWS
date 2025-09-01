from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.user import User
from app.utils import convert_utc_to_kst


@dataclass
class TokenPairDTO:
    access_token: str
    refresh_token: str


@dataclass
class UserDTO:
    id: int
    login_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    @classmethod
    def from_model(cls, user: User) -> "UserDTO":
        return cls(
            id=user.id,
            login_id=user.login_id,
            created_at=convert_utc_to_kst(user.created_at),
            updated_at=convert_utc_to_kst(user.updated_at),
            is_deleted=user.is_deleted,
        )
