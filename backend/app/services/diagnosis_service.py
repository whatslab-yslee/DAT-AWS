from datetime import datetime, timedelta
import io
import logging
from typing import List, Optional, Tuple
import uuid

from app.dtos.diagnosis_dto import DiagnosisDTO, DiagnosisResultDTO, DiagnosisStateDTO, DiagnosisTypeDTO
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.services.diagnosis_password_manager import DiagnosisPasswordManager
from app.services.diagnosis_result_process import DiagnosisResultProcessor
from app.services.s3_service import S3Service
from app.utils import get_datetime_from_timestamp, get_datetime_now, get_datetime_now_plus_timedelta, get_timestamp_now
from fastapi import UploadFile
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class DiagnosisService:
    ORIGINAL_FILE_PATH_TEMPLATE = "diagnosis/{diagnosis_id}/original/{filename}"
    PROCESSED_FILE_PATH_TEMPLATE = "diagnosis/{diagnosis_id}/processed/{filename}"
    # VIDEO_FILE_PATH_TEMPLATE = "diagnosis/{diagnosis_id}/video/{filename}"

    def __init__(
        self,
        repository: DiagnosisRepository,
        s3_service: S3Service,
        password_manager: DiagnosisPasswordManager,
        result_processor: DiagnosisResultProcessor,
    ):
        self.repository = repository
        self.s3_service = s3_service
        self.password_manager = password_manager
        self.result_processor = result_processor

    def is_session_expired(self, session_id: str) -> bool:
        """세션 ID에서 만료 시간을 파싱하여, 현재 세션이 만료되었는지 확인합니다.

        Args:
            session_id: 세션 ID (형식: {uuid}-{timestamp})

        Returns:
            bool: 세션 만료 여부 (True: 만료됨, False: 유효함)
        """
        try:
            # 세션 ID에서 타임스탬프 부분 추출
            parts = session_id.split("-")
            if len(parts) != 2:
                logger.error(f"잘못된 세션 ID 형식: {session_id}")
                return True  # 잘못된 형식은 만료된 것으로 처리

            # 타임스탬프를 정수로 변환
            expiry_timestamp = int(parts[1])
            current_timestamp = get_timestamp_now()

            # 만료 시간과 현재 시간 비교
            if current_timestamp > expiry_timestamp:
                logger.info(f"세션 만료됨: {session_id}, 만료시간: {get_datetime_from_timestamp(expiry_timestamp).isoformat()}")
                return True

            return False
        except Exception as e:
            logger.error(f"세션 만료 확인 중 오류 발생: {e}")
            return True  # 오류 발생 시 만료된 것으로 처리

    def start_diagnosis(
        self, db: Session, doctor_id: int, patient_id: int, type: DiagnosisTypeDTO, level: int, session_duration: timedelta = timedelta(minutes=30)
    ) -> DiagnosisDTO:
        """새 진단 시작"""
        diagnosis = self.repository.create_diagnosis(
            db,
            doctor_id=doctor_id,
            patient_id=patient_id,
            code=str(uuid.uuid4())[:6].upper(),
            type=type,
            state=DiagnosisStateDTO.READY,
            level=level,
            expired_at=get_datetime_now_plus_timedelta(session_duration),
        )
        return DiagnosisDTO.from_entity(diagnosis)

    def get_live_diagnosis_by_doctor_id(self, db: Session, doctor_id: int) -> Optional[DiagnosisDTO]:
        """의사 ID로 진행중인 진단 조회"""
        diagnosis = self.repository.get_live_diagnosis_by_doctor_id(db, doctor_id)
        if not diagnosis:
            logger.info(f"세션을 찾을 수 없음: 의사ID={doctor_id}")
            return None
        return DiagnosisDTO.from_entity(diagnosis)

    def get_diagnosis_by_id(self, db: Session, diagnosis_id: int) -> Optional[DiagnosisDTO]:
        """진단 조회"""
        diagnosis = self.repository.get_diagnosis_by_id(db, diagnosis_id)
        if not diagnosis:
            logger.info(f"진단을 찾을 수 없음: 진단ID={diagnosis_id}")
            return None
        return DiagnosisDTO.from_entity(diagnosis)

    def get_diagnosis_by_code(self, db: Session, code: str) -> Optional[DiagnosisDTO]:
        """진단 코드로 진단 조회"""
        diagnosis = self.repository.get_diagnosis_by_code(db, code)
        if not diagnosis:
            logger.info(f"진단을 찾을 수 없음: 진단코드={code}")
            return None
        return DiagnosisDTO.from_entity(diagnosis)

    def update_diagnosis_state(self, db: Session, diagnosis_id: int, state: DiagnosisStateDTO) -> Optional[DiagnosisStateDTO]:
        """진단 상태 업데이트"""
        updated_diagnosis = self.repository.update_state(db, diagnosis_id, state)
        if not updated_diagnosis:
            logger.warning(f"진단 상태 업데이트 실패: 진단ID={diagnosis_id}, 상태={state.value}")
            return None

        return DiagnosisStateDTO(updated_diagnosis.state.value)

    def upload_diagnosis_result(self, db: Session, diagnosis_id: int, diagnosis_type: DiagnosisTypeDTO, diagnosis_level: int, file: UploadFile) -> bool:
        """진단 결과 파일 업로드"""
        try:
            filename = f"{diagnosis_type.value}_{diagnosis_level}_{get_datetime_now().strftime('%Y%m%d%H%M%S')}.csv"

            # 원본 파일 S3 업로드
            original_file = file.file.read()
            original_file_path = self.ORIGINAL_FILE_PATH_TEMPLATE.format(diagnosis_id=diagnosis_id, filename=filename)
            self.s3_service.upload_file(original_file_path, io.BytesIO(original_file))

            # 전처리 및 S3 업로드
            processed_file, score = self.result_processor.preprocess(diagnosis_type, original_file)
            processed_file_path = self.PROCESSED_FILE_PATH_TEMPLATE.format(diagnosis_id=diagnosis_id, filename=filename)
            self.s3_service.upload_file(processed_file_path, io.BytesIO(processed_file))

            # 파일 정보 저장
            self.repository.create_diagnosis_result(db, diagnosis_id, original_file_path, processed_file_path, score.score, score.time_spent, score.fps)

            return True
        except Exception as e:
            logger.error(f"진단 결과 업로드 중 오류 발생: {str(e)}", exc_info=True)
            return False

    def get_diagnosis_record_metadata(self, db: Session, diagnosis_id: int) -> Optional[Tuple[DiagnosisDTO, DiagnosisResultDTO]]:
        """특정 진단 기록 메타데이터 조회"""
        record = self.repository.get_diagnosis_record(db, diagnosis_id)
        if not record:
            logger.info(f"진단 기록을 찾을 수 없음: 진단ID={diagnosis_id}")
            return None

        diagnosis, result = record
        return (DiagnosisDTO.from_entity(diagnosis), DiagnosisResultDTO.from_entity(result))

    def get_diagnosis_file(self, db: Session, diagnosis_id: int) -> Tuple[Optional[str], Optional[io.BytesIO]]:
        """특정 진단 기록 파일 경로 조회"""
        record = self.repository.get_diagnosis_record(db, diagnosis_id)
        if not record:
            logger.info(f"진단 기록을 찾을 수 없음: 진단ID={diagnosis_id}")
            return None, None

        _, result = record

        # S3 버킷 내 파일 경로
        s3_file_path = result.processed_file_path
        filename = s3_file_path.split("/")[-1]
        # 1. S3에서 파일 데이터 (bytes) 가져오기
        file_bytes = self.s3_service.get_file_data(s3_file_path)
        if file_bytes is None:
            return filename, None

        # 2. bytes 데이터를 BytesIO 객체로 변환
        bytesio_obj = io.BytesIO(file_bytes)
        return filename, bytesio_obj

    def get_patient_diagnosis_records(
        self, db: Session, patient_id: int, start_date: datetime, end_date: datetime
    ) -> List[Tuple[DiagnosisDTO, DiagnosisResultDTO]]:
        """환자의 진단 기록 리스트 조회"""
        records = self.repository.get_diagnosis_records_by_patient(db, patient_id, start_date, end_date)
        result_list = []
        for diagnosis, result in records:
            result_list.append(
                (
                    DiagnosisDTO.from_entity(diagnosis),
                    DiagnosisResultDTO.from_entity(result),
                )
            )
        return result_list
