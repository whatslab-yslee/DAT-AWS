import io
from typing import Annotated

from app.configs.database import get_db
from app.core.ws_connection_manager import manager
from app.dependency.dependency import get_diagnosis_service, get_patient_service
from app.dtos.diagnosis_dto import DiagnosisStateDTO
from app.schemas.ws_schema import (
    ClientDiagnosisFailedData,
    ClientDiagnosisStartedData,
    UploadResultData,
    WebSocketMessage,
    WebSocketMessageAction,
)
from app.services.diagnosis_service import DiagnosisService
from app.services.patient_service import PatientService
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.datastructures import UploadFile
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session


router = APIRouter(prefix="/ws", tags=["WebSocket"])

# TODO: 상수 별도 파일로 분리
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def _handle_diagnosis_started(db: Session, message: WebSocketMessage, diagnosis_service: DiagnosisService):
    """C_DIAGNOSIS_STARTED 액션을 처리합니다."""
    start_data = ClientDiagnosisStartedData.model_validate(message.data)
    diagnosis_service.update_diagnosis_state(db, start_data.diagnosis_id, DiagnosisStateDTO.STARTED)
    logger.info(f"Updated diagnosis {start_data.diagnosis_id} to STARTED")


def _handle_diagnosis_failed(db: Session, message: WebSocketMessage, diagnosis_service: DiagnosisService):
    """C_DIAGNOSIS_FAILED 액션을 처리합니다."""
    fail_data = ClientDiagnosisFailedData.model_validate(message.data)
    diagnosis_service.update_diagnosis_state(db, fail_data.diagnosis_id, DiagnosisStateDTO.FAILED)
    logger.info(f"Updated diagnosis {fail_data.diagnosis_id} to FAILED")


def _handle_upload_result(
    db: Session,
    message: WebSocketMessage,
    diagnosis_service: DiagnosisService,
    patient_id: int,
):
    """C_UPLOAD_RESULT 액션을 처리합니다."""
    upload_data = UploadResultData.model_validate(message.data)

    diagnosis_dto = diagnosis_service.get_diagnosis_by_id(db, upload_data.diagnosis_id)
    if not diagnosis_dto:
        logger.error(f"Diagnosis not found: {upload_data.diagnosis_id}")
        return
    if diagnosis_dto.patient_id != patient_id:
        logger.warning(f"Patient ID mismatch: {patient_id} vs {diagnosis_dto.patient_id}")
        return

    file_content_bytes = upload_data.file_content.encode("utf-8")

    if len(file_content_bytes) > MAX_FILE_SIZE_BYTES:
        logger.error(f"Uploaded file for diagnosis {upload_data.diagnosis_id} exceeds size limit of {MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB.")
        diagnosis_service.update_diagnosis_state(db, upload_data.diagnosis_id, DiagnosisStateDTO.FAILED)
        return

    file_object = io.BytesIO(file_content_bytes)
    temp_upload_file = UploadFile(file=file_object, filename=f"temp_result_{upload_data.diagnosis_id}.csv")

    diagnosis_service.upload_diagnosis_result(
        db,
        diagnosis_dto.id,
        diagnosis_dto.type,
        diagnosis_dto.level,
        temp_upload_file,
    )
    diagnosis_service.update_diagnosis_state(db, diagnosis_dto.id, DiagnosisStateDTO.COMPLETED)
    logger.info(f"Successfully processed result for diagnosis_id: {diagnosis_dto.id}")


@router.websocket("/diagnosis/{patient_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    patient_code: str,
    patient_service: PatientService = Depends(get_patient_service),
    db: Annotated[Session, Depends(get_db)] = None,
    diagnosis_service: DiagnosisService = Depends(get_diagnosis_service),
):
    patient = patient_service.get_patient_by_code(db, patient_code)
    if not patient:
        logger.warning(f"Patient with code '{patient_code}' not found. Closing WebSocket.")
        await websocket.close(code=4004)  # Custom close code for not found
        return

    patient_id = patient.id
    await manager.connect(patient_id, websocket)
    logger.info(f"WebSocket connected for patient_id: {patient_id} (code: {patient_code})")
    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = WebSocketMessage.model_validate(data)

                if message.action == WebSocketMessageAction.C_DIAGNOSIS_STARTED:
                    logger.info(f"Received diagnosis start acknowledgement for patient_id: {patient_id}")
                    _handle_diagnosis_started(db, message, diagnosis_service)

                elif message.action == WebSocketMessageAction.C_DIAGNOSIS_FAILED:
                    logger.info(f"Received diagnosis failure report for patient_id: {patient_id}")
                    _handle_diagnosis_failed(db, message, diagnosis_service)

                elif message.action == WebSocketMessageAction.C_UPLOAD_RESULT:
                    logger.info(f"Received upload result request for patient_id: {patient_id}")
                    _handle_upload_result(db, message, diagnosis_service, patient_id)

            except ValidationError as e:
                logger.error(f"WebSocket validation error for patient_id {patient_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing WebSocket message for patient_id {patient_id}: {e}")

    except WebSocketDisconnect:
        manager.disconnect(patient_id)
        logger.info(f"WebSocket disconnected for patient_id: {patient_id} (code: {patient_code})")
