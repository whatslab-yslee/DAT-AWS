from typing import Any, Optional, Tuple

from api_clients.schemas import ApiResponse
from pydantic import ValidationError
import requests


class BaseClient:
    """API 클라이언트의 기본 클래스"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = 5
        self.session = requests.Session()

    def _convert_to_model(self, data: dict, model_cls: type) -> Tuple[bool, Any, Optional[str], Optional[str]]:
        """API 응답 데이터를 Pydantic 모델로 변환합니다.

        Args:
            data: 변환할 데이터 딕셔너리
            model_cls: 변환할 모델 클래스

        Returns:
            Tuple: (성공 여부, 변환된 데이터 또는 None, 오류 메시지 또는 None, 오류 상세 정보 또는 None)
        """
        if not data or not model_cls:
            return True, data, None, None

        try:
            return True, model_cls(**data), None, None
        except ValidationError as e:
            return False, None, "응답 데이터 형식 오류", str(e)

    def _handle_response(self, response: requests.Response, model_cls: Optional[type] = None) -> "ApiResponse":
        """API 응답을 처리하여 ApiResponse 형태로 반환합니다.

        Args:
            response: requests 응답 객체
            model_cls: 응답 데이터를 변환할 Pydantic 모델 클래스

        Returns:
            ApiResponse: 처리된 API 응답
        """
        try:
            response.raise_for_status()
            data = response.json()

            # 모델 클래스로 변환
            if model_cls:
                success, converted_data, error, details = self._convert_to_model(data, model_cls)
                if not success:
                    return ApiResponse(success=False, error=error, details=details)
                data = converted_data

            return ApiResponse(success=True, data=data, status_code=response.status_code)
        except requests.RequestException as e:
            status_code = e.response.status_code if e.response is not None else None
            error_msg = "API 요청 오류"
            details = str(e)

            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                except ValueError:
                    # 응답이 JSON이 아닐 경우, 응답 텍스트를 상세 정보로 사용
                    details = e.response.text

            return ApiResponse(success=False, error=error_msg, details=details, status_code=status_code)
