from datetime import datetime

from app.dtos.diagnosis_dto import DiagnosisStateDTO, DiagnosisTypeDTO
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class DiagnosisBase(BaseModel):
    id: int = Field(..., description="진단 ID", json_schema_extra={"example": 1})


# 웹 -> 서버 진단 세션 생성
class DiagnosisCreate(BaseModel):
    patient_id: int = Field(..., description="환자 ID")
    type: DiagnosisTypeDTO = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")


class DiagnosisCreateResponse(DiagnosisBase):
    code: str = Field(..., description="진단 코드")
    expired_at: datetime = Field(..., description="세션 만료 시간")


class DiagnosisLiveResponse(DiagnosisBase):
    code: str = Field(..., description="진단 코드")
    expired_at: datetime = Field(..., description="세션 만료 시간")


# 서버 -> 웹 진단 세션 종료
class DiagnosisStateResponse(BaseModel):
    id: int
    state: DiagnosisStateDTO = Field(..., description="진단 상태")
    timestamp: datetime


# VR Client -> 서버 진단 세션 입장
class DiagnosisJoin(BaseModel):
    code: str = Field(..., description="진단 코드")


class DiagnosisJoinResponse(DiagnosisBase):
    type: DiagnosisTypeDTO = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")


# VR Client -> 서버 진단 결과 업로드
class DiagnosisUploadForm:
    def __init__(self, id: int = Form(..., description="진단 ID"), file: UploadFile = File(..., description="CSV 파일")):
        self.id = id
        self.file = file


# 특정 진단 기록 상세 조회
class DiagnosisRecordRequest(DiagnosisBase):
    pass


class DiagnosisRecordResponse(BaseModel):
    patient_id: int = Field(..., description="환자 ID")
    type: DiagnosisTypeDTO = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")
    created_at: datetime = Field(..., description="진단 생성 시간")
    filename: str = Field(..., description="결과 파일명")
    score: float = Field(..., description="결과 점수")
    time_spent: float = Field(..., description="결과 소요 시간")
    fps: float = Field(..., description="결과 프레임 수")
    # CSV 파일은 별도 엔드포인트로 FileResponse 반환


# 환자의 진단 기록 리스트 조회
class DiagnosisRecordListRequest(BaseModel):
    patient_id: int = Field(..., description="환자 ID")
    start_date: datetime = Field(..., description="조회 시작 날짜")
    end_date: datetime = Field(..., description="조회 종료 날짜")


class DiagnosisRecordListResponse(DiagnosisBase):
    type: DiagnosisTypeDTO = Field(..., description="진단 콘텐츠 타입")
    level: int = Field(..., description="진단 레벨")
    filename: str = Field(..., description="결과 파일명")
    created_at: datetime = Field(..., description="진단 생성 시간")
