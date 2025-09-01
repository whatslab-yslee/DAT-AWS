from datetime import datetime
from typing import Any, Dict

from app.configs.database import Base
from app.utils import get_datetime_now
from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: get_datetime_now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: get_datetime_now(), onupdate=lambda: get_datetime_now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
