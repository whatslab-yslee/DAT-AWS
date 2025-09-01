from enum import Enum
from typing import Optional

from app.dtos.diagnosis_dto import DiagnosisTypeDTO
from pydantic import BaseModel, Field


class WebSocketMessageAction(str, Enum):
    # Server -> Client
    S_START_DIAGNOSIS = "s_start_diagnosis"
    S_STOP_DIAGNOSIS = "s_stop_diagnosis"
    S_FORCE_DISCONNECT = "s_force_disconnect"

    # Client -> Server
    C_UPLOAD_RESULT = "c_upload_result"
    C_DIAGNOSIS_STARTED = "c_diagnosis_started"
    C_DIAGNOSIS_FAILED = "c_diagnosis_failed"


class WebSocketMessage(BaseModel):
    action: WebSocketMessageAction
    data: Optional[dict] = None


class StartDiagnosisData(BaseModel):
    diagnosis_id: int = Field(..., description="진단 ID", json_schema_extra={"example": 1})
    type: DiagnosisTypeDTO = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")


class UploadResultData(BaseModel):
    diagnosis_id: int = Field(..., description="진단 ID")
    file_content: str = Field(..., description="CSV 파일 내용 (문자열)")


class ClientDiagnosisStartedData(BaseModel):
    diagnosis_id: int = Field(..., description="진단 ID")


class ClientDiagnosisFailedData(BaseModel):
    diagnosis_id: int = Field(..., description="진단 ID")
