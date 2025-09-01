import asyncio
from datetime import timedelta
import json
from typing import Annotated

from app.configs.database import get_db
from app.controllers.auth_controller import get_user_from_token
from app.core.ws_connection_manager import manager
from app.dependency.dependency import get_diagnosis_service
from app.dtos.diagnosis_dto import DiagnosisDTO, DiagnosisStateDTO
from app.dtos.user_dto import UserDTO, UserRoleDTO
from app.schemas.diagnosis_schema import (
    DiagnosisCreate,
    DiagnosisCreateResponse,
    DiagnosisLiveResponse,
    DiagnosisStateResponse,
)
from app.schemas.ws_schema import StartDiagnosisData, WebSocketMessage, WebSocketMessageAction
from app.services.diagnosis_service import DiagnosisService
from app.services.doctor_service import DoctorService
from app.utils import get_datetime_now
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session


# TODO: 상수 별도 파일로 분리
MONITOR_INTERVAL = 5  # 상태 조회 간격 (초)
SESSION_DURATION = 30 * 60  # 세션 지속 시간 (초)

# 웹 인터페이스용 라우터 (JWT 기반 인증)
router = APIRouter(prefix="/diagnosis", tags=["diagnosis_web"])


@router.post(
    "/start",
    response_model=DiagnosisCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="진단 시작",
    description="새로운 진단 세션을 시작합니다.",
)
async def start_diagnosis(
    diagnosis_data: DiagnosisCreate,
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """진단 시작"""
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단을 시작할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 환자가 로그인 상태인지 확인
    if diagnosis_data.patient_id not in manager.active_connections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="환자가 로그인 상태가 아닙니다.")

    # 진행중인 진단 세션이 있는지 확인
    diagnosis = service.get_live_diagnosis_by_doctor_id(db, doctor.id)
    if diagnosis:
        raise HTTPException(status_code=400, detail="진행중인 진단 세션이 있습니다")

    new_diagnosis: DiagnosisDTO = service.start_diagnosis(
        db,
        doctor_id=doctor.id,
        patient_id=diagnosis_data.patient_id,
        type=diagnosis_data.type,
        level=diagnosis_data.level,
        session_duration=timedelta(seconds=SESSION_DURATION),
    )

    if not new_diagnosis:
        raise HTTPException(status_code=400, detail="진단 시작 중 오류가 발생했습니다")

    # WebSocket을 통해 VR 클라이언트에 진단 시작 알림
    message = WebSocketMessage(
        action=WebSocketMessageAction.S_START_DIAGNOSIS,
        data=StartDiagnosisData(diagnosis_id=new_diagnosis.id, type=new_diagnosis.type, level=new_diagnosis.level).model_dump(),
    )
    await manager.send_personal_message(message.model_dump(), new_diagnosis.patient_id)

    return DiagnosisCreateResponse(
        id=new_diagnosis.id,
        code=new_diagnosis.code,
        expired_at=new_diagnosis.expired_at,
    )


@router.get(
    "/live",
    response_model=DiagnosisLiveResponse,
    summary="진행중인 진단 세션 확인",
    description="진행중인 진단 세션을 확인합니다.",
)
async def get_live_diagnosis(
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """진행중인 진단 세션 확인"""
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단 세션을 확인할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 진행중인 진단 세션 반환
    diagnosis = service.get_live_diagnosis_by_doctor_id(db, doctor.id)
    if not diagnosis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="진행중인 진단 세션을 찾을 수 없습니다.")
    return DiagnosisLiveResponse(
        id=diagnosis.id,
        code=diagnosis.code,
        expired_at=diagnosis.expired_at,
    )


@router.post(
    "/{diagnosis_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="진단 취소",
    description="진단을 취소합니다.",
)
async def cancel_diagnosis(
    diagnosis_id: int,
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """진단 취소"""
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단을 취소할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 진단 정보 조회
    diagnosis_dto = service.get_diagnosis_by_id(db, diagnosis_id)
    if not diagnosis_dto:
        raise HTTPException(status_code=404, detail="진단을 찾을 수 없습니다")

    if diagnosis_dto.doctor_id != doctor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="해당 진단에 대한 권한이 없습니다.")

    if diagnosis_dto.state in [DiagnosisStateDTO.COMPLETED, DiagnosisStateDTO.FAILED, DiagnosisStateDTO.CANCELLED, DiagnosisStateDTO.EXPIRED]:
        raise HTTPException(status_code=400, detail="이미 완료된 진단입니다.")

    service.update_diagnosis_state(db, diagnosis_id, DiagnosisStateDTO.CANCELLED)

    # WebSocket을 통해 VR 클라이언트에 진단 종료(취소) 알림
    message = WebSocketMessage(action=WebSocketMessageAction.S_STOP_DIAGNOSIS)
    await manager.send_personal_message(message.model_dump(), diagnosis_dto.patient_id)

    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/{diagnosis_id}/status",
    response_model=DiagnosisStateResponse,
    summary="진단 상태 확인 (SSE)",
    description="진단의 상태 변화를 Server-Sent Events로 수신합니다.",
)
async def get_diagnosis_status(  # noqa: C901
    diagnosis_id: int,
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """진단 상태 변화를 SSE로 전송"""

    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단 상태를 확인할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 진단 정보 조회
    diagnosis_dto = service.get_diagnosis_by_id(db, diagnosis_id)
    if not diagnosis_dto:
        raise HTTPException(status_code=404, detail="진단을 찾을 수 없습니다")

    if diagnosis_dto.doctor_id != doctor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="해당 진단에 대한 권한이 없습니다.")

    async def event_generator():
        try:
            while True:
                # 최신 진단 상태 조회
                diagnosis_dto = service.get_diagnosis_by_id(db, diagnosis_id)
                if not diagnosis_dto:
                    yield f"data: {json.dumps({'error': '진단을 찾을 수 없습니다'})}\n\n"
                    break

                # 세션 만료 체크
                if diagnosis_dto.expired_at < get_datetime_now():
                    diagnosis_dto.state = service.update_diagnosis_state(db, diagnosis_id, DiagnosisStateDTO.EXPIRED)

                # 상태 전송
                state_data = {
                    "id": diagnosis_dto.id,
                    "state": diagnosis_dto.state.value,
                    "timestamp": diagnosis_dto.updated_at.isoformat(),
                }
                yield f"data: {json.dumps(state_data)}\n\n"

                # 종료 조건 확인
                if diagnosis_dto.state in [DiagnosisStateDTO.COMPLETED, DiagnosisStateDTO.FAILED, DiagnosisStateDTO.CANCELLED, DiagnosisStateDTO.EXPIRED]:
                    break

                await asyncio.sleep(MONITOR_INTERVAL)
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Content-Type": "text/event-stream", "X-Accel-Buffering": "no"},
    )
