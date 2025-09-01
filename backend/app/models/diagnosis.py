from datetime import datetime
from enum import Enum

from app.models.base_model import BaseModel
from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class DiagnosisType(str, Enum):
    NONE = "NONE"
    BALANCEBALL = "BALANCEBALL"
    FITBOX = "FITBOX"
    TENNISBALL = "TENNISBALL"


class DiagnosisState(str, Enum):
    READY = "READY"  # 준비
    STARTED = "STARTED"  # 진행
    CANCELLED = "CANCELLED"  # 취소
    FAILED = "FAILED"  # 실패
    COMPLETED = "COMPLETED"  # 완료
    EXPIRED = "EXPIRED"  # 만료


class Diagnosis(BaseModel):
    __tablename__ = "diagnoses"

    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[DiagnosisType] = mapped_column(SQLAlchemyEnum(DiagnosisType), default=DiagnosisType.NONE, nullable=False)
    level: Mapped[int] = mapped_column(nullable=False)
    state: Mapped[DiagnosisState] = mapped_column(SQLAlchemyEnum(DiagnosisState), default=DiagnosisState.READY, nullable=False)
    expired_at: Mapped[datetime] = mapped_column(nullable=False)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "doctor_id": self.doctor_id,
                "patient_id": self.patient_id,
                "code": self.code,
                "type": self.type.value,
                "level": self.level,
                "state": self.state.value,
                "expired_at": self.expired_at,
            }
        )
        return base_dict


class DiagnosisResult(BaseModel):
    __tablename__ = "diagnosis_results"

    diagnosis_id: Mapped[int] = mapped_column(ForeignKey("diagnoses.id"), nullable=False)
    original_file_path: Mapped[str] = mapped_column(nullable=False)
    processed_file_path: Mapped[str] = mapped_column(nullable=True)
    score: Mapped[float] = mapped_column(nullable=True)
    time_spent: Mapped[float] = mapped_column(nullable=True)
    fps: Mapped[float] = mapped_column(nullable=True)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "diagnosis_id": self.diagnosis_id,
                "original_file_path": self.original_file_path,
                "processed_file_path": self.processed_file_path,
                "score": self.score,
                "time_spent": self.time_spent,
                "fps": self.fps,
            }
        )
        return base_dict
