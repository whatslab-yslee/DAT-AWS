from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.utils import convert_utc_to_kst


class DiagnosisStateDTO(str, Enum):
    READY = "READY"  # 준비
    STARTED = "STARTED"  # 진행
    CANCELLED = "CANCELLED"  # 취소 (서버 중단 요청)
    FAILED = "FAILED"  # 실패 (클라이언트 종료)
    COMPLETED = "COMPLETED"  # 완료
    EXPIRED = "EXPIRED"  # 만료


class DiagnosisTypeDTO(str, Enum):
    NONE = "NONE"
    BALANCEBALL = "BALANCEBALL"
    FITBOX = "FITBOX"
    TENNISBALL = "TENNISBALL"


@dataclass
class DiagnosisDTO:
    id: int
    doctor_id: int
    patient_id: int
    code: str
    type: DiagnosisTypeDTO
    level: int
    state: DiagnosisStateDTO
    expired_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity):
        if not entity:
            return None
        return cls(
            id=entity.id,
            doctor_id=entity.doctor_id,
            patient_id=entity.patient_id,
            code=entity.code,
            type=entity.type,
            level=entity.level,
            state=entity.state,
            expired_at=convert_utc_to_kst(entity.expired_at),
            created_at=convert_utc_to_kst(entity.created_at),
            updated_at=convert_utc_to_kst(entity.updated_at),
        )


@dataclass
class DiagnosisResultDTO:
    id: int
    diagnosis_id: int
    original_file_path: str
    processed_file_path: str
    score: float
    time_spent: float
    fps: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity):
        if not entity:
            return None
        return cls(
            id=entity.id,
            diagnosis_id=entity.diagnosis_id,
            original_file_path=entity.original_file_path,
            processed_file_path=entity.processed_file_path,
            score=entity.score,
            time_spent=entity.time_spent,
            fps=entity.fps,
            created_at=convert_utc_to_kst(entity.created_at),
            updated_at=convert_utc_to_kst(entity.updated_at),
        )
