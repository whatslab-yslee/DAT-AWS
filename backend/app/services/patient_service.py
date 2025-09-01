from typing import List, Union

from app.dtos.patient_dto import PatientDTO
from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from sqlalchemy.orm import Session


MAX_PATIENT_COUNT = 999


# TODO: static method 대신 의존성 주입을 위한 instance method 사용
class PatientService:
    @staticmethod
    def create_patient(db: Session, doctor_id: int, name: str, code: str = None) -> PatientDTO:
        """환자 생성"""
        patient_cnt = PatientRepository.count_by_doctor_id(db, doctor_id)
        if patient_cnt > MAX_PATIENT_COUNT:
            raise Exception(f"의사당 최대 환자 수 초과 (doctor_id: {doctor_id})")

        if not code:
            doctor_no = f"{doctor_id:03d}"[-3:]
            patient_no = f"{patient_cnt:03d}"[:3]
            code = f"{doctor_no}-{patient_no}"

        patient = Patient(created_by=doctor_id, name=name, code=code)
        created_patient = PatientRepository.create(db, patient)
        return PatientDTO.from_model(created_patient)

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Union[PatientDTO, None]:
        """ID로 환자 조회"""
        patient = PatientRepository.find_by_id(db, patient_id)
        if not patient:
            return None
        return PatientDTO.from_model(patient)

    @staticmethod
    def get_patient_by_code(db: Session, code: str) -> Union[PatientDTO, None]:
        """코드로 환자 조회"""
        patient = PatientRepository.find_by_code(db, code)
        if not patient:
            return None
        return PatientDTO.from_model(patient)

    @staticmethod
    def get_patients_by_doctor(db: Session, doctor_id: int) -> List[PatientDTO]:
        """의사가 등록한 환자 목록 조회"""
        patients = PatientRepository.find_by_doctor_id(db, doctor_id)
        return [PatientDTO.from_model(patient) for patient in patients]

    @staticmethod
    def update_patient(db: Session, patient_id: int, updates: dict) -> Union[PatientDTO, None]:
        """환자 정보 업데이트"""
        patient = PatientRepository.find_by_id(db, patient_id)
        if not patient:
            return None
        updated_patient = PatientRepository.update(db, patient, updates)
        return PatientDTO.from_model(updated_patient)

    @staticmethod
    def delete_patient(db: Session, patient_id: int) -> bool:
        """환자 삭제"""
        patient = PatientRepository.find_by_id(db, patient_id)
        if not patient:
            return False
        return PatientRepository.delete(db, patient)

    @staticmethod
    def is_patient_owned_by_doctor(db: Session, patient_id: int, doctor_id: int) -> bool:
        """의사가 해당 환자의 담당의인지 확인"""
        patient = PatientRepository.find_by_id(db, patient_id)
        if not patient:
            return False
        return patient.created_by == doctor_id
