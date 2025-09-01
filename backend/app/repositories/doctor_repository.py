from typing import Union

from app.models.doctor import Doctor
from sqlalchemy.orm import Session


class DoctorRepository:
    @staticmethod
    def create(db: Session, doctor: Doctor) -> Doctor:
        """의사 생성"""
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def find_by_id(db: Session, doctor_id: int) -> Union[Doctor, None]:
        """ID로 의사 찾기"""
        return db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.is_deleted.is_(False)).first()

    @staticmethod
    def find_by_user_id(db: Session, user_id: int) -> Union[Doctor, None]:
        """사용자 ID로 의사 찾기"""
        return db.query(Doctor).filter(Doctor.user_id == user_id, Doctor.is_deleted.is_(False)).first()

    @staticmethod
    def update(db: Session, doctor: Doctor, updates: dict) -> Doctor:
        """의사 정보 업데이트"""
        for key, value in updates.items():
            if hasattr(doctor, key) and key != "id" and key != "user_id":
                setattr(doctor, key, value)

        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def delete(db: Session, doctor: Doctor) -> bool:
        """의사 삭제"""
        doctor.is_deleted = True
        db.commit()
        return True
