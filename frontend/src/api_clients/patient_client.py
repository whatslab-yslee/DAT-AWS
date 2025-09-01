from typing import List, Optional

from api_clients.base_client import BaseClient
from api_clients.schemas import ApiResponse, PatientCreate, PatientResponse, PatientUpdate
from config import get_settings


settings = get_settings()


class PatientClient(BaseClient):
    """환자 API 클라이언트"""

    def __init__(self, base_url: str, token: Optional[str] = None):
        super().__init__(base_url)
        self.token = token
        self.base_endpoint = "/patients"

    def set_token(self, token: str) -> None:
        """인증 토큰을 설정합니다.

        Args:
            token: 인증 토큰
        """
        self.token = token

    def _get_headers(self) -> dict:
        """요청 헤더를 생성합니다.

        Returns:
            dict: 요청 헤더
        """
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _process_patient_list(self, response_data: List[dict]) -> List[PatientResponse]:
        """환자 목록 데이터를 PatientResponse 객체 리스트로 변환합니다.

        Args:
            response_data: API 응답 데이터 리스트

        Returns:
            List[PatientResponse]: 변환된 환자 응답 객체 리스트
        """
        result = []
        for item in response_data:
            try:
                patient = PatientResponse(**item)
                result.append(patient)
            except Exception as e:
                print(f"환자 데이터 변환 오류: {str(e)}")
        return result

    def get_patients(self) -> ApiResponse:
        """의사가 등록한 환자 목록을 조회합니다.

        Returns:
            ApiResponse: API 응답 (성공 시 data=List[PatientResponse])
        """
        endpoint = f"{self.base_url}{self.base_endpoint}"
        response = self.session.get(endpoint, headers=self._get_headers(), timeout=self.timeout)

        try:
            response.raise_for_status()
            data = response.json()

            # 데이터가 리스트인 경우 별도 처리
            if isinstance(data, list):
                patients = self._process_patient_list(data)
                return ApiResponse(success=True, data=patients)

            return ApiResponse(success=True, data=data)
        except Exception as e:
            return ApiResponse(success=False, error="환자 목록 조회 중 오류가 발생했습니다", details=str(e))

    def create_patient(self, name: str, code: Optional[str] = None) -> ApiResponse:
        """환자를 생성합니다.

        Args:
            name: 환자 이름
            code: 환자 코드 (선택적)

        Returns:
            ApiResponse: API 응답 (성공 시 data=PatientResponse)
        """
        endpoint = f"{self.base_url}{self.base_endpoint}"
        patient_data = PatientCreate(name=name, code=code)

        response = self.session.post(endpoint, json=patient_data.model_dump(exclude_none=True), headers=self._get_headers(), timeout=self.timeout)

        try:
            response.raise_for_status()
            data = response.json()

            try:
                patient = PatientResponse(**data)
                return ApiResponse(success=True, data=patient)
            except Exception as e:
                return ApiResponse(success=False, error="환자 데이터 형식 오류", details=str(e))
        except Exception as e:
            return ApiResponse(success=False, error="환자 생성 중 오류가 발생했습니다", details=str(e))

    def update_patient(self, patient_id: int, name: str, code: Optional[str] = None) -> ApiResponse:
        """환자 정보를 수정합니다.

        Args:
            patient_id: 환자 ID
            name: 환자 이름
            code: 환자 코드 (선택적)

        Returns:
            ApiResponse: API 응답 (성공 시 data=PatientResponse)
        """
        endpoint = f"{self.base_url}{self.base_endpoint}/{patient_id}"
        patient_data = PatientUpdate(name=name)

        response = self.session.put(endpoint, json=patient_data.model_dump(exclude_none=True), headers=self._get_headers(), timeout=self.timeout)

        try:
            response.raise_for_status()
            data = response.json()

            try:
                patient = PatientResponse(**data)
                return ApiResponse(success=True, data=patient)
            except Exception as e:
                return ApiResponse(success=False, error="환자 데이터 형식 오류", details=str(e))
        except Exception as e:
            return ApiResponse(success=False, error="환자 정보 수정 중 오류가 발생했습니다", details=str(e))

    def delete_patient(self, patient_id: int) -> ApiResponse:
        """환자를 삭제합니다.

        Args:
            patient_id: 환자 ID

        Returns:
            ApiResponse: API 응답
        """
        endpoint = f"{self.base_url}{self.base_endpoint}/{patient_id}"

        response = self.session.delete(endpoint, headers=self._get_headers(), timeout=self.timeout)

        try:
            response.raise_for_status()
            return ApiResponse(success=True)
        except Exception as e:
            return ApiResponse(success=False, error="환자 삭제 중 오류가 발생했습니다", details=str(e))


_patient_client_instance: Optional[PatientClient] = None


def get_patient_client(base_url: str = settings.API_BASE_URL, token: Optional[str] = None) -> PatientClient:
    """환자 API 클라이언트를 반환합니다.

    Args:
        base_url: API 기본 URL
        token: 인증 토큰 (선택적)

    Returns:
        PatientClient: 환자 API 클라이언트
    """
    global _patient_client_instance
    if _patient_client_instance is None:
        _patient_client_instance = PatientClient(base_url, token)
    return _patient_client_instance
