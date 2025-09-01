from typing import List, Union

from app.models.patient import Patient
from sqlalchemy.orm import Session


class PatientRepository:
    @staticmethod
    def create(db: Session, patient: Patient) -> Patient:
        """환자 생성"""
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def find_by_id(db: Session, patient_id: int) -> Union[Patient, None]:
        """ID로 환자 찾기"""
        return db.query(Patient).filter(Patient.id == patient_id, Patient.is_deleted.is_(False)).first()

    @staticmethod
    def find_by_code(db: Session, code: str) -> Union[Patient, None]:
        """코드로 환자 찾기"""
        return db.query(Patient).filter(Patient.code == code, Patient.is_deleted.is_(False)).first()

    @staticmethod
    def find_by_doctor_id(db: Session, doctor_id: int) -> List[Patient]:
        """의사가 등록한 환자 목록 찾기"""
        return db.query(Patient).filter(Patient.created_by == doctor_id, Patient.is_deleted.is_(False)).all()

    @staticmethod
    def count_by_doctor_id(db: Session, doctor_id: int) -> int:
        """의사가 등록한 환자 수 찾기"""
        return db.query(Patient).filter(Patient.created_by == doctor_id, Patient.is_deleted.is_(False)).count()

    @staticmethod
    def update(db: Session, patient: Patient, updates: dict) -> Patient:
        """환자 정보 업데이트"""
        for key, value in updates.items():
            if hasattr(patient, key) and key != "id" and key != "code" and key != "created_by":
                setattr(patient, key, value)

        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def delete(db: Session, patient: Patient) -> bool:
        """환자 삭제"""
        patient.is_deleted = True
        db.commit()
        return True
