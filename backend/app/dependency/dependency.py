from functools import lru_cache

from app.repositories.diagnosis_repository import DiagnosisRepository
from app.services.diagnosis_password_manager import DiagnosisPasswordManager
from app.services.diagnosis_result_process import DiagnosisResultProcessor
from app.services.diagnosis_service import DiagnosisService
from app.services.patient_service import PatientService
from app.services.s3_service import S3Service
from fastapi import Depends


# 리포지토리 의존성 제공 함수
@lru_cache()
def get_diagnosis_repository() -> DiagnosisRepository:
    return DiagnosisRepository()


# S3 서비스 의존성 제공 함수
@lru_cache()
def get_s3_service() -> S3Service:
    return S3Service()


# 진단 비밀번호 관리자 의존성 제공 함수
@lru_cache()
def get_diagnosis_password_manager() -> DiagnosisPasswordManager:
    return DiagnosisPasswordManager()


# 진단 결과 처리 의존성 제공 함수
@lru_cache()
def get_diagnosis_result_processor() -> DiagnosisResultProcessor:
    return DiagnosisResultProcessor()


# 진단 서비스 의존성 제공 함수
def get_diagnosis_service(
    repository: DiagnosisRepository = Depends(get_diagnosis_repository),
    s3_service: S3Service = Depends(get_s3_service),
    password_manager: DiagnosisPasswordManager = Depends(get_diagnosis_password_manager),
    result_processor: DiagnosisResultProcessor = Depends(get_diagnosis_result_processor),
) -> DiagnosisService:
    return DiagnosisService(repository=repository, s3_service=s3_service, password_manager=password_manager, result_processor=result_processor)


def get_patient_service() -> PatientService:
    return PatientService()
