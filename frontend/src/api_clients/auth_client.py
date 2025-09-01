from typing import Optional

from api_clients.base_client import BaseClient
from api_clients.schemas import ApiResponse, TokenRefresh, TokenResponse, UserCreate, UserLogin, UserResponse
from config import get_settings
from utils import delete_browser_cookie, get_browser_cookie, set_browser_cookie


settings = get_settings()


class AuthClient(BaseClient):
    """인증 관련 API를 호출하는 클라이언트 클래스"""

    def __init__(self, base_url: str = settings.API_BASE_URL):
        super().__init__(base_url)
        self.auth_url = f"{base_url}/auth"

    def register(self, login_id: str, password: str, name: str, role: str) -> ApiResponse:
        """사용자 회원가입

        Args:
            login_id: 사용자 로그인 ID
            password: 사용자 비밀번호

        Returns:
            ApiResponse: API 응답 (성공 시 data=UserResponse)
        """
        user_data = UserCreate(login_id=login_id, password=password, name=name, role=role)

        try:
            response = self.session.post(f"{self.auth_url}/register", json=user_data.model_dump(), timeout=self.timeout)
            return self._handle_response(response, UserResponse)
        except Exception as e:
            return ApiResponse(success=False, error="회원가입 중 오류가 발생했습니다", details=str(e))

    def login(self, login_id: str, password: str) -> ApiResponse:
        """사용자 로그인

        Args:
            login_id: 사용자 로그인 ID
            password: 사용자 비밀번호

        Returns:
            ApiResponse: API 응답 (성공 시 data=TokenResponse)
        """
        user_data = UserLogin(login_id=login_id, password=password)

        try:
            response = self.session.post(f"{self.auth_url}/login", json=user_data.model_dump(), timeout=self.timeout)
            result = self._handle_response(response, TokenResponse)

            # 로그인 성공 시 refresh_token을 쿠키에 저장
            if result.success and result.data and result.data.refresh_token:
                set_browser_cookie("refresh_token", result.data.refresh_token, 30)

            return result
        except Exception as e:
            return ApiResponse(success=False, error="로그인 중 오류가 발생했습니다", details=str(e))

    def logout(self, access_token: str) -> ApiResponse:
        """사용자 로그아웃

        Args:
            access_token: 액세스 토큰

        Returns:
            ApiResponse: API 응답
        """
        try:
            response = self.session.post(f"{self.auth_url}/logout", headers={"Authorization": f"Bearer {access_token}"}, timeout=self.timeout)
            # 로그아웃 시 쿠키에서 refresh_token 삭제
            delete_browser_cookie("refresh_token")

            if response.status_code == 200:
                return ApiResponse(success=True, data=None)
            else:
                return ApiResponse(success=False, error=f"로그아웃 실패: {response.status_code}", details=response.text)
        except Exception as e:
            return ApiResponse(success=False, error="로그아웃 중 오류가 발생했습니다", details=str(e))

    def refresh_token(self) -> ApiResponse:
        """액세스 토큰 갱신

        Args:
            refresh_token: 리프레시 토큰

        Returns:
            ApiResponse: API 응답 (성공 시 data=TokenResponse)
        """
        refresh_token = get_browser_cookie("refresh_token")
        if not refresh_token:
            return ApiResponse(success=False, error="리프레시 토큰이 없습니다")

        token_refresh = TokenRefresh(refresh_token=refresh_token)
        try:
            response = self.session.post(f"{self.auth_url}/refresh", json=token_refresh.model_dump(), timeout=self.timeout, allow_redirects=False)
            result = self._handle_response(response, TokenResponse)

            # 성공적으로 토큰이 갱신되었고 응답에 새 refresh_token이 있는 경우 저장
            if result.success and result.data and result.data.refresh_token:
                set_browser_cookie("refresh_token", result.data.refresh_token, 30)

            return result
        except Exception as e:
            return ApiResponse(success=False, error="토큰 갱신 중 오류가 발생했습니다", details=str(e))

    def get_user_info(self, access_token: str) -> ApiResponse:
        """현재 인증된 사용자 정보 조회

        Args:
            access_token: 액세스 토큰

        Returns:
            ApiResponse: API 응답 (성공 시 data=UserResponse)
        """
        try:
            response = self.session.get(f"{self.auth_url}/me", headers={"Authorization": f"Bearer {access_token}"}, timeout=self.timeout)
            return self._handle_response(response, UserResponse)
        except Exception as e:
            return ApiResponse(success=False, error="사용자 정보 조회 중 오류가 발생했습니다", details=str(e))


_auth_client_instance: Optional[AuthClient] = None


def get_auth_client(base_url: str = settings.API_BASE_URL) -> AuthClient:
    global _auth_client_instance
    if _auth_client_instance is None:
        _auth_client_instance = AuthClient(base_url=base_url)
    return _auth_client_instance
