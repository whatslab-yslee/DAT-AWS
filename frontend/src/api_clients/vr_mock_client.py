"""
VR 클라이언트를 모킹하는 API 클라이언트 모듈입니다.
진단 세션 입장 및 결과 업로드 기능을 제공합니다.
"""

from io import BytesIO
from typing import Optional

from api_clients.schemas import ApiResponse, DiagnosisJoin, DiagnosisJoinResponse, DiagnosisUploadRequest
from config import get_settings
import requests


class VRMockClient:
    """VR 클라이언트를 모킹하는 API 클라이언트 클래스"""

    def __init__(self):
        """클라이언트 초기화"""
        self.settings = get_settings()
        self.base_url = f"{self.settings.API_BASE_URL}/diagnosis"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "VR-Client/1.0"})

    def join_diagnosis(self, code: str) -> ApiResponse:
        """진단 세션에 입장합니다.

        Args:
            code: 진단 코드

        Returns:
            ApiResponse: API 응답 (성공 시 data=DiagnosisJoinResponse)
        """
        try:
            url = f"{self.base_url}/join"
            data = DiagnosisJoin(code=code)
            response = self.session.post(url, json=data.model_dump())

            if response.status_code == 200:
                try:
                    response_data = DiagnosisJoinResponse(**response.json())
                    return ApiResponse(success=True, data=response_data)
                except Exception as e:
                    return ApiResponse(success=False, error="응답 데이터 형식 오류", details=str(e))
            else:
                return ApiResponse(success=False, error=f"요청 실패: {response.status_code}", details=response.text)
        except Exception as e:
            return ApiResponse(success=False, error="오류 발생", details=str(e))

    def upload_diagnosis_result(self, id: int, result_data: Optional[BytesIO] = None) -> ApiResponse:
        """진단 결과를 업로드합니다.

        Args:
            id: 진단 ID
            result_data: 진단 결과 데이터 (바이너리)

        Returns:
            ApiResponse: API 응답
        """
        try:
            url = f"{self.base_url}/result"

            # 결과 데이터가 없는 경우
            if result_data is None:
                file_path = "assets/data/테스트_BalanceBall_1_20250124142555.csv"
                with open(file_path, "rb") as f:
                    result_data = BytesIO(f.read())
                    result_data.name = "테스트_BalanceBall_1_20250124142555.csv"

            # 파일 업로드
            files = {"file": (getattr(result_data, "name", "result.csv"), result_data, "text/csv")}
            data = DiagnosisUploadRequest(id=id)

            response = self.session.put(url, files=files, data=data.model_dump())

            if response.status_code == 200:
                return ApiResponse(success=True)
            else:
                return ApiResponse(success=False, error=f"업로드 실패: {response.status_code}", details=response.text)
        except Exception as e:
            return ApiResponse(success=False, error="오류 발생", details=str(e))


def get_vr_mock_client() -> VRMockClient:
    """VR 모킹 클라이언트의 인스턴스를 반환합니다."""
    return VRMockClient()
