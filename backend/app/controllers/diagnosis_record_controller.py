from datetime import datetime
import io
from typing import Annotated, List
import urllib.parse

from app.configs.database import get_db
from app.controllers.auth_controller import get_user_from_token
from app.dependency.dependency import get_diagnosis_service
from app.dtos.user_dto import UserDTO, UserRoleDTO
from app.schemas.diagnosis_schema import (
    DiagnosisRecordListResponse,
    DiagnosisRecordResponse,
)
from app.services.diagnosis_service import DiagnosisService
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session


# 웹 인터페이스용 라우터 (JWT 기반 인증)
router = APIRouter(prefix="/diagnosis/record", tags=["diagnosis_record"])


# BytesIO에서 데이터를 읽어 비동기적으로 yield하는 제너레이터
async def stream_from_bytesio(bytesio_obj: io.BytesIO):
    chunk_size = 8192  # 적절한 청크 크기
    # BytesIO는 동기 read를 가짐. 실제 사용 시 run_in_threadpool 고려
    # from fastapi.concurrency import run_in_threadpool
    while chunk := bytesio_obj.read(chunk_size):
        # await run_in_threadpool(bytesio_obj.read, chunk_size) # 실제 사용 시
        yield chunk


@router.get(
    "/{diagnosis_id}/metadata",
    response_model=DiagnosisRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="특정 진단 기록 메타데이터 조회",
    description="진단 ID로 특정 진단 기록의 메타데이터를 조회합니다.",
)
async def get_diagnosis_record_metadata(
    diagnosis_id: int,
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """특정 진단 기록 메타데이터 조회"""
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단 기록을 조회할 수 있습니다.")

    # 진단 기록 메타데이터 조회
    result = service.get_diagnosis_record_metadata(db, diagnosis_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="진단 기록을 찾을 수 없습니다.")

    diagnosis_dto, result_dto = result
    filename = result_dto.processed_file_path.split("/")[-1]

    return DiagnosisRecordResponse(
        patient_id=diagnosis_dto.patient_id,
        type=diagnosis_dto.type,
        level=diagnosis_dto.level,
        created_at=diagnosis_dto.created_at,
        filename=filename,
        score=result_dto.score,
        time_spent=result_dto.time_spent,
        fps=result_dto.fps,
    )


@router.get(
    "/{diagnosis_id}/file",
    status_code=status.HTTP_302_FOUND,
    summary="특정 진단 기록 파일 다운로드",
    description="진단 ID로 특정 진단 기록의 CSV 파일을 다운로드합니다.",
)
async def download_diagnosis_file(
    diagnosis_id: int,
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """특정 진단 기록 파일 다운로드"""
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단 기록을 다운로드할 수 있습니다.")

    # 파일 데이터 조회
    filename, file_bytes = service.get_diagnosis_file(db, diagnosis_id)
    if not filename or not file_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="진단 파일을 찾을 수 없습니다.")

    # 한글 파일명을 위한 인코딩 처리
    encoded_filename = urllib.parse.quote(filename)

    return StreamingResponse(
        content=stream_from_bytesio(file_bytes),  # BytesIO를 읽는 제너레이터 사용
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{encoded_filename}"'
            # Content-Length: len(file_bytes)
        },
    )


@router.get(
    "/list",
    response_model=List[DiagnosisRecordListResponse],
    status_code=status.HTTP_200_OK,
    summary="환자의 진단 기록 리스트 조회",
    description="환자 ID와 기간으로 진단 기록 목록을 조회합니다.",
)
async def get_patient_diagnosis_records(
    patient_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: Annotated[UserDTO, Depends(get_user_from_token)],
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """환자의 진단 기록 리스트 조회"""
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 진단 기록을 조회할 수 있습니다.")

    # 진단 기록 목록 조회
    records = service.get_patient_diagnosis_records(db, patient_id, start_date, end_date)

    # 결과 변환
    response_list = []
    for diagnosis_dto, result_dto in records:
        filename = result_dto.processed_file_path.split("/")[-1]
        response_list.append(
            DiagnosisRecordListResponse(
                id=diagnosis_dto.id, type=diagnosis_dto.type, level=diagnosis_dto.level, filename=filename, created_at=diagnosis_dto.created_at
            )
        )

    return response_list
