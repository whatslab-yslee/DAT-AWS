from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.patient import Patient
from app.utils import convert_utc_to_kst


@dataclass
class PatientDTO:
    id: int
    name: str
    code: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    @classmethod
    def from_model(cls, patient: Patient) -> "PatientDTO":
        return cls(
            id=patient.id,
            name=patient.name,
            code=patient.code,
            created_by=patient.created_by,
            created_at=convert_utc_to_kst(patient.created_at),
            updated_at=convert_utc_to_kst(patient.updated_at),
            is_deleted=patient.is_deleted,
        )
