from app.models.base_model import BaseModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class Token(BaseModel):
    __tablename__ = "tokens"

    refresh_token: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "refresh_token": self.refresh_token,
                "user_id": self.user_id,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
            }
        )
        return base_dict
