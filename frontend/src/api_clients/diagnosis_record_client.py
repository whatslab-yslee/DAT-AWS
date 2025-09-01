from datetime import datetime
import io
from typing import Optional, Tuple

from api_clients.base_client import BaseClient
from api_clients.schemas import (
    ApiResponse,
    DiagnosisRecordListResponse,
    DiagnosisRecordResponse,
)
from config import get_settings
import pandas as pd


settings = get_settings()


class DiagnosisRecordClient(BaseClient):
    """진단 기록 관련 API를 호출하는 클라이언트 클래스"""

    def __init__(self, base_url: str = settings.API_BASE_URL):
        super().__init__(base_url)
        self.diagnosis_record_url = f"{base_url}/diagnosis/record"
        self._token = None

    def set_token(self, token: str):
        """인증 토큰 설정

        Args:
            token: 액세스 토큰
        """
        self._token = token

    def get_patient_diagnosis_records(self, patient_id: int, start_date: datetime, end_date: datetime) -> ApiResponse:
        """환자의 진단 기록 목록을 조회합니다.

        Args:
            patient_id: 환자 ID
            start_date: 조회 시작 날짜
            end_date: 조회 종료 날짜

        Returns:
            ApiResponse: API 응답 (성공 시 data=List[DiagnosisRecordListResponse])
        """
        if not self._token:
            return ApiResponse(success=False, error="인증 토큰이 필요합니다")

        try:
            params = {"patient_id": patient_id, "start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            headers = {"Authorization": f"Bearer {self._token}"}

            response = self.session.get(f"{self.diagnosis_record_url}/list", params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # 리스트 응답 수동 처리
            records_data = response.json()
            if not isinstance(records_data, list):
                return ApiResponse(success=False, error="예상치 못한 응답 형식", details="API 응답이 리스트 형식이 아닙니다.")

            # 각 레코드를 DiagnosisRecordListResponse 모델로 변환
            records = []
            for record_data in records_data:
                try:
                    record = DiagnosisRecordListResponse(**record_data)
                    records.append(record)
                except Exception as e:
                    print(f"레코드 변환 오류: {str(e)}, 데이터: {record_data}")
                    # 오류가 있어도 계속 진행

            return ApiResponse(success=True, data=records)
        except Exception as e:
            error_details = str(e)
            return ApiResponse(success=False, error=f"진단 기록 목록 조회 중 오류: {type(e).__name__}, {error_details}", details=error_details)

    def get_diagnosis_record_metadata(self, diagnosis_id: int) -> ApiResponse:
        """특정 진단 기록의 메타데이터를 조회합니다.

        Args:
            diagnosis_id: 진단 ID

        Returns:
            ApiResponse: API 응답 (성공 시 data=DiagnosisRecordResponse)
        """
        if not self._token:
            return ApiResponse(success=False, error="인증 토큰이 필요합니다")

        try:
            headers = {"Authorization": f"Bearer {self._token}"}

            response = self.session.get(f"{self.diagnosis_record_url}/{diagnosis_id}/metadata", headers=headers, timeout=self.timeout)
            return self._handle_response(response, DiagnosisRecordResponse)
        except Exception as e:
            error_details = str(e)
            return ApiResponse(success=False, error=f"진단 기록 메타데이터 조회 중 오류: {type(e).__name__}", details=error_details)

    def download_diagnosis_file(self, diagnosis_id: int) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
        """특정 진단 기록의 CSV 파일을 다운로드합니다.

        Args:
            diagnosis_id: 진단 ID

        Returns:
            Tuple[Optional[str], Optional[pd.DataFrame]]: (파일명, DataFrame) 튜플 또는 오류 시 (None, None)
        """
        if not self._token:
            return None, None

        try:
            headers = {"Authorization": f"Bearer {self._token}"}

            response = self.session.get(
                f"{self.diagnosis_record_url}/{diagnosis_id}/file",
                headers=headers,
                stream=True,
                timeout=None,  # 파일 다운로드는 시간이 오래 걸릴 수 있음
            )
            response.raise_for_status()

            # 파일명 추출
            content_disposition = response.headers.get("Content-Disposition", "")
            filename = None
            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')

            # CSV 파일을 DataFrame으로 변환
            csv_content = response.content
            df = pd.read_csv(io.BytesIO(csv_content))

            return filename, df
        except Exception as e:
            print(f"진단 파일 다운로드 중 오류: {str(e)}")
            return None, None


_diagnosis_record_client_instance: Optional[DiagnosisRecordClient] = None


def get_diagnosis_record_client(base_url: str = settings.API_BASE_URL) -> DiagnosisRecordClient:
    """DiagnosisRecordClient의 싱글톤 인스턴스를 반환합니다.

    Args:
        base_url: API 베이스 URL (기본값: 설정에서 가져옴)

    Returns:
        DiagnosisRecordClient: 클라이언트 인스턴스
    """
    global _diagnosis_record_client_instance
    if _diagnosis_record_client_instance is None:
        _diagnosis_record_client_instance = DiagnosisRecordClient(base_url=base_url)
    return _diagnosis_record_client_instance
