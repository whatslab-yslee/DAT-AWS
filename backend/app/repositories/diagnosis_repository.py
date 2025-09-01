from datetime import datetime
import logging
from typing import List, Optional, Tuple

from app.dtos.diagnosis_dto import DiagnosisStateDTO, DiagnosisTypeDTO
from app.models.diagnosis import Diagnosis, DiagnosisResult, DiagnosisState, DiagnosisType
from app.utils import get_datetime_now
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class DiagnosisRepository:
    def __init__(self):
        pass

    def create_diagnosis(
        self,
        db: Session,
        doctor_id: int,
        patient_id: int,
        code: str,
        type: DiagnosisTypeDTO,
        state: DiagnosisStateDTO,
        level: int,
        expired_at: datetime,
    ) -> Diagnosis:
        """새로운 진단 생성"""
        diagnosis = Diagnosis(
            doctor_id=doctor_id,
            patient_id=patient_id,
            code=code,
            type=DiagnosisType[type.value],
            state=DiagnosisState[state.value],
            level=level,
            expired_at=expired_at,
        )
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return diagnosis

    def get_diagnosis_by_id(self, db: Session, diagnosis_id: int) -> Optional[Diagnosis]:
        """ID로 진단 조회"""
        return db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()

    def get_diagnosis_by_code(self, db: Session, code: str) -> Optional[Diagnosis]:
        """코드로 진단 조회"""
        try:
            query = db.query(Diagnosis).filter(Diagnosis.code == code)
            return query.first()
        except Exception as e:
            logger.error(f"진단 조회 중 오류 발생: {e}")
            return None

    def get_live_diagnosis_by_doctor_id(self, db: Session, doctor_id: int) -> Optional[Diagnosis]:
        """의사 ID로 진행중인 진단 조회"""
        diagnosis = db.query(Diagnosis).filter(Diagnosis.doctor_id == doctor_id, Diagnosis.state.in_([DiagnosisState.STARTED, DiagnosisState.READY])).first()
        if not diagnosis:
            logger.info(f"진단 자체가 없음... doctor_id: {doctor_id}")
            return None
        return diagnosis

    def update_state(self, db: Session, diagnosis_id: int, state: DiagnosisStateDTO) -> Optional[Diagnosis]:
        """진단 상태 업데이트"""
        diagnosis = self.get_diagnosis_by_id(db, diagnosis_id)
        if not diagnosis:
            return None

        model_state = DiagnosisState[state.value]
        diagnosis.state = model_state
        diagnosis.updated_at = get_datetime_now()
        db.commit()
        db.refresh(diagnosis)
        return diagnosis

    def create_diagnosis_result(
        self,
        db: Session,
        diagnosis_id: int,
        original_file_path: str,
        processed_file_path: str,
        score: float,
        time_spent: float,
        fps: float,
    ) -> DiagnosisResult:
        """진단 결과 파일 정보 생성"""
        result = DiagnosisResult(
            diagnosis_id=diagnosis_id,
            original_file_path=original_file_path,
            processed_file_path=processed_file_path,
            score=score,
            time_spent=time_spent,
            fps=fps,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    def get_results_by_diagnosis_id(self, db: Session, diagnosis_id: int) -> List[DiagnosisResult]:
        """진단 ID로 결과 목록 조회"""
        return db.query(DiagnosisResult).filter(DiagnosisResult.diagnosis_id == diagnosis_id).all()

    def get_diagnosis_record(self, db: Session, diagnosis_id: int) -> Optional[Tuple[Diagnosis, DiagnosisResult]]:
        """특정 진단 기록 상세 조회"""
        diagnosis = self.get_diagnosis_by_id(db, diagnosis_id)
        if not diagnosis:
            return None

        # 진단 결과 조회 (첫 번째 결과만 반환)
        result = db.query(DiagnosisResult).filter(DiagnosisResult.diagnosis_id == diagnosis_id).first()
        if not result:
            return None

        return diagnosis, result

    def get_diagnosis_records_by_patient(
        self, db: Session, patient_id: int, start_date: datetime, end_date: datetime
    ) -> List[Tuple[Diagnosis, DiagnosisResult]]:
        """환자의 진단 기록 리스트 조회"""
        try:
            # 환자의 진단 목록 조회
            diagnoses = (
                db.query(Diagnosis)
                .filter(
                    Diagnosis.patient_id == patient_id,
                    Diagnosis.created_at >= start_date,
                    Diagnosis.created_at <= end_date,
                    Diagnosis.state == DiagnosisState.COMPLETED,  # 완료된 진단만 조회
                )
                .order_by(Diagnosis.created_at.desc())
                .all()
            )

            result_list = []
            for diagnosis in diagnoses:
                # 각 진단의 결과 조회
                result = db.query(DiagnosisResult).filter(DiagnosisResult.diagnosis_id == diagnosis.id).first()
                if result:
                    result_list.append((diagnosis, result))

            return result_list
        except Exception as e:
            logger.error(f"환자 진단 기록 조회 중 오류 발생: {e}")
            return []
