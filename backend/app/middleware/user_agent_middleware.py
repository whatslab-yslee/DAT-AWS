import logging
from typing import Annotated, Callable, List, Optional

from app.configs.env_configs import get_settings
from fastapi import Header, HTTPException, Request, status
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)

settings = get_settings()
VR_CLIENT_USER_AGENTS = settings.VR_CLIENT_USER_AGENTS


class UserAgentMiddleware:
    """
    User-Agent 기반 API 요청 필터링 미들웨어

    지정된 User-Agent만 허용하거나 차단하는 미들웨어입니다.
    """

    def __init__(self, allowed_user_agents: Optional[List[str]] = None, blocked_user_agents: Optional[List[str]] = None):
        """
        Args:
            allowed_user_agents: 허용할 User-Agent 목록 (None이면 모든 User-Agent 허용)
            blocked_user_agents: 차단할 User-Agent 목록
        """
        self.allowed_user_agents = allowed_user_agents or []
        self.blocked_user_agents = blocked_user_agents or []

    async def __call__(self, request: Request, call_next: Callable):
        user_agent = request.headers.get("user-agent", "")

        # 차단 목록에 있는 User-Agent 검사
        for blocked_agent in self.blocked_user_agents:
            if blocked_agent in user_agent:
                logger.warning(f"차단된 User-Agent 접근 시도: {user_agent}")
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "올바르지 않은 접근입니다."})

        # 허용 목록에 있는지 검사
        if self.allowed_user_agents:
            is_allowed = False
            for allowed_agent in self.allowed_user_agents:
                if allowed_agent in user_agent:
                    is_allowed = True
                    break
            if not is_allowed:
                logger.warning(f"허용되지 않은 User-Agent 접근 시도: {user_agent}")
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "올바르지 않은 접근입니다."})

        response = await call_next(request)
        return response


def vr_client_user_agent_verifier() -> Callable:
    return create_user_agent_verifier(allowed_user_agents=VR_CLIENT_USER_AGENTS)


def create_user_agent_verifier(allowed_user_agents: Optional[List[str]] = None, blocked_user_agents: Optional[List[str]] = None) -> Callable:
    """설정 값을 받아 User-Agent 검증 의존성 함수를 생성하는 팩토리 함수"""

    final_allowed = allowed_user_agents or []
    final_blocked = blocked_user_agents or []

    def _verify_user_agent(user_agent: Annotated[Optional[str], Header()] = None):
        ua = user_agent or ""

        for blocked in final_blocked:
            if blocked in ua:
                logger.warning(f"차단된 User-Agent 접근 시도: {ua}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="올바르지 않은 접근입니다.")

        if final_allowed:
            is_allowed = False
            for allowed in final_allowed:
                if allowed in ua:
                    is_allowed = True
                    break
            if not is_allowed:
                logger.warning(f"허용되지 않은 User-Agent 접근 시도: {ua}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="올바르지 않은 접근입니다.")

    return _verify_user_agent
