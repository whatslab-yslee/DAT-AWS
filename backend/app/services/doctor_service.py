from typing import Union

from app.dtos.doctor_dto import DoctorDTO
from app.models.doctor import Doctor
from app.repositories.doctor_repository import DoctorRepository
from sqlalchemy.orm import Session


class DoctorService:
    @staticmethod
    def create_doctor(db: Session, user_id: int) -> DoctorDTO:
        """의사 생성"""
        doctor = Doctor(user_id=user_id)
        created_doctor = DoctorRepository.create(db, doctor)
        return DoctorDTO.from_model(created_doctor)

    @staticmethod
    def get_doctor_by_id(db: Session, doctor_id: int) -> Union[DoctorDTO, None]:
        """ID로 의사 조회"""
        doctor = DoctorRepository.find_by_id(db, doctor_id)
        if not doctor:
            return None
        return DoctorDTO.from_model(doctor)

    @staticmethod
    def get_doctor_by_user_id(db: Session, user_id: int) -> Union[DoctorDTO, None]:
        """사용자 ID로 의사 조회"""
        doctor = DoctorRepository.find_by_user_id(db, user_id)
        if not doctor:
            return None
        return DoctorDTO.from_model(doctor)

    @staticmethod
    def update_doctor(db: Session, doctor_id: int, updates: dict) -> Union[DoctorDTO, None]:
        """의사 정보 업데이트"""
        doctor = DoctorRepository.find_by_id(db, doctor_id)
        if not doctor:
            return None
        updated_doctor = DoctorRepository.update(db, doctor, updates)
        return DoctorDTO.from_model(updated_doctor)

    @staticmethod
    def delete_doctor(db: Session, doctor_id: int) -> bool:
        """의사 삭제"""
        doctor = DoctorRepository.find_by_id(db, doctor_id)
        if not doctor:
            return False
        return DoctorRepository.delete(db, doctor)
