from typing import Optional

from api_clients.base_client import BaseClient
from api_clients.schemas import (
    ApiResponse,
    DiagnosisCreate,
    DiagnosisCreateResponse,
    DiagnosisLiveResponse,
)
from config import get_settings


settings = get_settings()


class DiagnosisClient(BaseClient):
    """진단 관련 API를 호출하는 클라이언트 클래스"""

    def __init__(self, base_url: str = settings.API_BASE_URL):
        super().__init__(base_url)
        self.diagnosis_url = f"{base_url}/diagnosis"
        self._token = None

    def set_token(self, token: str):
        """인증 토큰 설정

        Args:
            token: 액세스 토큰
        """
        self._token = token

    def start_diagnosis(self, patient_id: int, diagnosis_type: str, level: int) -> ApiResponse:
        """진단 시작

        Args:
            patient_id: 환자 ID
            diagnosis_type: 진단 콘텐츠 타입
            level: 진단 레벨

        Returns:
            ApiResponse: API 응답 (성공 시 data=DiagnosisCreateResponse)
        """
        if not self._token:
            return ApiResponse(success=False, error="인증 토큰이 필요합니다")

        request_data = DiagnosisCreate(patient_id=patient_id, type=diagnosis_type, level=level)
        headers = {"Authorization": f"Bearer {self._token}"}
        response = self.session.post(f"{self.diagnosis_url}/start", json=request_data.model_dump(), headers=headers, timeout=self.timeout)

        return self._handle_response(response, DiagnosisCreateResponse)

    def get_diagnosis_status(self, diagnosis_id: int) -> ApiResponse:
        """진단 상태 확인

        Args:
            diagnosis_id: 진단 ID

        Returns:
            ApiResponse: API 응답 - SSE 응답을 처리하기 위한 원시 응답 객체 반환
        """
        if not self._token:
            return ApiResponse(success=False, error="인증 토큰이 필요합니다")

        try:
            response = self.session.get(
                f"{self.diagnosis_url}/{diagnosis_id}/status",
                headers={"Authorization": f"Bearer {self._token}"},
                stream=True,
                timeout=None,
            )

            if response.status_code != 200:
                error_msg = f"진단 상태 확인 실패 ({response.status_code})"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_msg = f"진단 상태 확인 실패 ({response.status_code}): {error_data['detail']}"
                except Exception:
                    error_msg = f"진단 상태 확인 실패 ({response.status_code}): {response.text}"
                return ApiResponse(success=False, error=error_msg)

            return ApiResponse(success=True, data=response)
        except Exception as e:
            error_details = str(e)
            return ApiResponse(success=False, error=f"진단 상태 확인 중 오류: {type(e).__name__}", details=error_details)

    def get_live_diagnosis(self) -> ApiResponse:
        """진행중인 진단 조회

        Returns:
            ApiResponse: API 응답 (성공 시 data=DiagnosisLiveResponse)
        """
        if not self._token:
            return ApiResponse(success=False, error="인증 토큰이 필요합니다")
        try:
            headers = {"Authorization": f"Bearer {self._token}"}
            response = self.session.get(f"{self.diagnosis_url}/live", headers=headers, timeout=self.timeout)
            return self._handle_response(response, DiagnosisLiveResponse)
        except Exception as e:
            error_details = str(e)
            return ApiResponse(success=False, error=f"진행중인 진단 세션 조회 중 오류: {type(e).__name__}", details=error_details)

    def cancel_diagnosis(self, diagnosis_id: int) -> ApiResponse:
        """진단 취소"""
        if not self._token:
            return ApiResponse(success=False, error="인증 토큰이 필요합니다")
        try:
            headers = {"Authorization": f"Bearer {self._token}"}
            response = self.session.post(
                f"{self.diagnosis_url}/{diagnosis_id}/cancel",
                headers=headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return ApiResponse(success=True)
            else:
                return ApiResponse(success=False, error=f"진단 취소 처리 실패: {response.status_code}")
        except Exception as e:
            return ApiResponse(success=False, error=f"진단 취소 처리 중 오류: {type(e).__name__}", details=str(e))


_diagnosis_client_instance: Optional[DiagnosisClient] = None


def get_diagnosis_client(base_url: str = settings.API_BASE_URL) -> DiagnosisClient:
    global _diagnosis_client_instance
    if _diagnosis_client_instance is None:
        _diagnosis_client_instance = DiagnosisClient(base_url=base_url)
    return _diagnosis_client_instance
