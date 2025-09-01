import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.middleware.user_agent_middleware import UserAgentMiddleware, create_user_agent_verifier
from fastapi import Depends, FastAPI
from fastapi.routing import APIRouter
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def test_app():
    app = FastAPI()
    router = APIRouter()

    # 테스트 라우트 추가
    @router.get("/test")
    async def test_route():
        return {"message": "테스트 통과"}

    # 라우터 등록
    app.include_router(router)

    return app


@pytest.fixture
def test_app_with_dependency():
    app = FastAPI()
    router = APIRouter()

    # 테스트 라우트 추가 - 의존성 없음
    @router.get("/test")
    async def test_route():
        return {"message": "테스트 통과"}

    # 의존성이 적용된 보호된 라우트
    @router.get("/protected", dependencies=[Depends(create_user_agent_verifier(allowed_user_agents=["VRClient"]))])
    async def protected_route():
        return {"message": "보호된 리소스 접근 성공"}

    # 의존성이 적용된 차단 라우트
    @router.get("/blocked", dependencies=[Depends(create_user_agent_verifier(blocked_user_agents=["curl"]))])
    async def blocked_route():
        return {"message": "차단 목록 테스트 성공"}

    # 라우터 등록
    app.include_router(router)

    return app


def test_allowed_user_agent(test_app):
    """허용된 User-Agent로 요청 시 정상 처리되는지 테스트"""
    # 미들웨어 등록
    test_app.middleware("http")(UserAgentMiddleware(allowed_user_agents=["VRClient"], blocked_user_agents=["curl"]))

    client = TestClient(test_app, raise_server_exceptions=False)

    # 허용된 User-Agent로 요청
    response = client.get("/test", headers={"User-Agent": "VRClient/1.0"})

    assert response.status_code == 200
    assert response.json() == {"message": "테스트 통과"}


def test_blocked_user_agent(test_app):
    """차단된 User-Agent로 요청 시 403 반환되는지 테스트"""
    # 미들웨어 등록
    test_app.middleware("http")(UserAgentMiddleware(allowed_user_agents=["VRClient"], blocked_user_agents=["curl", "Postman"]))

    client = TestClient(test_app, raise_server_exceptions=False)

    # 차단된 User-Agent로 요청
    response = client.get("/test", headers={"User-Agent": "curl/7.68.0"})

    assert response.status_code == 403
    assert "올바르지 않은 접근입니다." in response.text


def test_disallowed_user_agent(test_app):
    """허용 목록에 없는 User-Agent로 요청 시 403 반환되는지 테스트"""
    # 미들웨어 등록
    test_app.middleware("http")(
        UserAgentMiddleware(
            allowed_user_agents=["VRClient", "Unity"],
        )
    )

    client = TestClient(test_app, raise_server_exceptions=False)

    # 허용 목록에 없는 User-Agent로 요청
    response = client.get("/test", headers={"User-Agent": "Mozilla/5.0"})

    assert response.status_code == 403
    assert "올바르지 않은 접근입니다." in response.text


def test_only_blocked_list(test_app):
    """허용 목록 없이 차단 목록만 적용했을 때 테스트"""
    # 미들웨어 등록
    test_app.middleware("http")(UserAgentMiddleware(blocked_user_agents=["curl", "Postman"]))

    client = TestClient(test_app, raise_server_exceptions=False)

    # 차단되지 않은 User-Agent로 요청
    response = client.get("/test", headers={"User-Agent": "Mozilla/5.0"})

    assert response.status_code == 200
    assert response.json() == {"message": "테스트 통과"}


# create_user_agent_verifier 함수 테스트
def test_dependency_allowed_user_agent(test_app_with_dependency):
    """의존성 주입 방식으로 허용된 User-Agent로 요청 시 정상 처리되는지 테스트"""
    client = TestClient(test_app_with_dependency, raise_server_exceptions=False)

    # 허용된 User-Agent로 보호된 라우트 요청
    response = client.get("/protected", headers={"User-Agent": "VRClient/1.0"})

    assert response.status_code == 200
    assert response.json() == {"message": "보호된 리소스 접근 성공"}


def test_dependency_disallowed_user_agent(test_app_with_dependency):
    """의존성 주입 방식으로 허용 목록에 없는 User-Agent로 요청 시 403 반환되는지 테스트"""
    client = TestClient(test_app_with_dependency, raise_server_exceptions=False)

    # 허용되지 않은 User-Agent로 보호된 라우트 요청
    response = client.get("/protected", headers={"User-Agent": "Mozilla/5.0"})

    assert response.status_code == 403
    assert "올바르지 않은 접근입니다." in response.text


def test_dependency_blocked_user_agent(test_app_with_dependency):
    """의존성 주입 방식으로 차단된 User-Agent로 요청 시 403 반환되는지 테스트"""
    client = TestClient(test_app_with_dependency, raise_server_exceptions=False)

    # 차단된 User-Agent로 차단 라우트 요청
    response = client.get("/blocked", headers={"User-Agent": "curl/7.68.0"})

    assert response.status_code == 403
    assert "올바르지 않은 접근입니다." in response.text


def test_dependency_normal_user_agent(test_app_with_dependency):
    """의존성 주입 방식으로 차단되지 않은 User-Agent로 요청 시 정상 처리되는지 테스트"""
    client = TestClient(test_app_with_dependency, raise_server_exceptions=False)

    # 차단되지 않은 User-Agent로 차단 라우트 요청
    response = client.get("/blocked", headers={"User-Agent": "Mozilla/5.0"})

    assert response.status_code == 200
    assert response.json() == {"message": "차단 목록 테스트 성공"}
