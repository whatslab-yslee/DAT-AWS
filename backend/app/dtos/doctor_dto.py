from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.doctor import Doctor
from app.utils import convert_utc_to_kst


@dataclass
class DoctorDTO:
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    @classmethod
    def from_model(cls, doctor: Doctor) -> "DoctorDTO":
        return cls(
            id=doctor.id,
            user_id=doctor.user_id,
            created_at=convert_utc_to_kst(doctor.created_at),
            updated_at=convert_utc_to_kst(doctor.updated_at),
            is_deleted=doctor.is_deleted,
        )
