from enum import Enum

from app.models.base_model import BaseModel
from sqlalchemy import Boolean, Enum as SQLAlchemyEnum, String
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(str, Enum):
    NONE = "NONE"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    PATIENT = "PATIENT"


class User(BaseModel):
    __tablename__ = "users"

    login_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole),
        default=UserRole.NONE,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "login_id": self.login_id,
                "name": self.name,
                "role": self.role.value,
                "is_verified": self.is_verified,
            }
        )
        return base_dict
