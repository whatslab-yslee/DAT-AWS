from app.models.base_model import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Doctor(BaseModel):
    __tablename__ = "doctors"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return base_dict
