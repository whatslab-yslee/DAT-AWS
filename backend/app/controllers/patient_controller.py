from typing import List

from app.configs.database import get_db
from app.controllers.auth_controller import get_user_from_token
from app.dtos.user_dto import UserDTO, UserRoleDTO
from app.schemas.patient_schema import PatientCreate, PatientResponse, PatientUpdate
from app.services.doctor_service import DoctorService
from app.services.patient_service import PatientService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db), current_user: UserDTO = Depends(get_user_from_token)):
    """환자 생성 API

    의사만 환자를 생성할 수 있습니다.
    """
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 환자를 생성할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 환자 생성
    try:
        patient = PatientService.create_patient(db=db, doctor_id=doctor.id, name=patient_data.name, code=patient_data.code)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return PatientResponse(
        id=patient.id, code=patient.code, name=patient.name, created_at=patient.created_at.isoformat(), updated_at=patient.updated_at.isoformat()
    )


@router.get("", response_model=List[PatientResponse])
def get_doctor_patients(db: Session = Depends(get_db), current_user: UserDTO = Depends(get_user_from_token)):
    """의사가 등록한 환자 목록 조회 API

    의사만 본인이 등록한 환자 목록을 조회할 수 있습니다.
    """
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 환자 목록을 조회할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 환자 목록 조회
    patients = PatientService.get_patients_by_doctor(db, doctor.id)

    return [
        PatientResponse(
            id=patient.id,
            code=patient.code,
            name=patient.name,
            created_at=patient.created_at.isoformat(),
            updated_at=patient.updated_at.isoformat(),
        )
        for patient in patients
    ]


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_data: PatientUpdate, db: Session = Depends(get_db), current_user: UserDTO = Depends(get_user_from_token)):
    """환자 정보 업데이트 API

    의사만 본인이 등록한 환자 정보를 업데이트할 수 있습니다.
    """
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 환자 정보를 업데이트할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 환자가 존재하는지 확인
    patient = PatientService.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")

    # 의사가 해당 환자의 담당의인지 확인
    if not PatientService.is_patient_owned_by_doctor(db, patient_id, doctor.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="다른 의사가 등록한 환자 정보는 수정할 수 없습니다.")

    # 업데이트할 필드만 딕셔너리로 구성
    updates = {}
    if patient_data.name is not None:
        updates["name"] = patient_data.name

    # 환자 정보 업데이트
    updated_patient = PatientService.update_patient(db, patient_id, updates)

    return PatientResponse(
        id=updated_patient.id,
        code=updated_patient.code,
        name=updated_patient.name,
        created_at=updated_patient.created_at.isoformat(),
        updated_at=updated_patient.updated_at.isoformat(),
    )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: UserDTO = Depends(get_user_from_token)):
    """환자 삭제 API

    의사만 본인이 등록한 환자를 삭제할 수 있습니다.
    """
    # 의사 권한 확인
    if current_user.role != UserRoleDTO.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의사만 환자를 삭제할 수 있습니다.")

    # 현재 사용자의 의사 정보 조회
    doctor = DoctorService.get_doctor_by_user_id(db, current_user.id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="의사 정보를 찾을 수 없습니다.")

    # 환자가 존재하는지 확인
    patient = PatientService.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")

    # 의사가 해당 환자의 담당의인지 확인
    if not PatientService.is_patient_owned_by_doctor(db, patient_id, doctor.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="다른 의사가 등록한 환자는 삭제할 수 없습니다.")

    # 환자 삭제
    PatientService.delete_patient(db, patient_id)

    return None
