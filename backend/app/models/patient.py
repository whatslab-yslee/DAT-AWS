from app.models.base_model import BaseModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class Patient(BaseModel):
    __tablename__ = "patients"

    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "code": self.code,
                "name": self.name,
                "created_by": self.created_by,
            }
        )
        return base_dict
