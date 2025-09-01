from typing import Annotated

from app.configs.database import get_db
from app.dtos.user_dto import UserDTO, UserLoginDTO, UserRegistrationInputDTO
from app.schemas.auth_schema import TokenRefresh, TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session


security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_user_from_token(token: str = Depends(security), db: Session = Depends(get_db)) -> UserDTO:
    token_str = token.credentials if token else None

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 제공되지 않았습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_dto = AuthService.get_user_from_token(db, token_str)
    if not user_dto:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_dto


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 회원가입",
    description="새로운 사용자를 등록합니다.",
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    try:
        # Service로 전달할 DTO 생성
        registration_data = UserRegistrationInputDTO(
            login_id=user_data.login_id,
            password=user_data.password,
            name=user_data.name,  # 이름 정보 추가
            role=user_data.role,
            admin_code=user_data.admin_code,
        )

        # Service의 register_user 호출 (이제 DTO를 받음)
        created_user_dto = AuthService.register_user(db, registration_data)

        # Service가 반환한 DTO를 사용하여 응답 생성
        return UserResponse(
            id=created_user_dto.id,
            login_id=created_user_dto.login_id,
            name=created_user_dto.name,
            role=created_user_dto.role,
            created_at=created_user_dto.created_at,
            updated_at=created_user_dto.updated_at,
        )
    except ValueError as e:  # Service에서 발생시킨 특정 예외 처리 (예: ID 중복)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:  # 기타 예상치 못한 오류 처리
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"사용자 등록 중 오류가 발생했습니다. {e}")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="사용자 로그인",
    description="JSON 형식으로 로그인 요청을 처리하고 Access Token을 반환합니다. Refresh Token은 HttpOnly 쿠키로 설정됩니다.",
)
async def login(response: Response, request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    login_input = UserLoginDTO(login_id=user_data.login_id, password=user_data.password)
    user_dto = AuthService.authenticate_user(db, login_input)

    if not user_dto:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인 ID 또는 비밀번호가 일치하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = AuthService.create_tokens(db, user_dto.id, client_ip, user_agent)

    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/logout", summary="로그아웃", description="현재 사용자의 모든 Refresh Token을 삭제하여 로그아웃 처리합니다.")
async def logout(response: Response, current_user: Annotated[UserDTO, Depends(get_user_from_token)], db: Session = Depends(get_db)):
    """사용자 로그아웃"""
    AuthService.logout_user(db, current_user.id)
    response.delete_cookie(key="refresh_token", path="/auth/refresh")

    return Response(status_code=status.HTTP_200_OK)


@router.post("/refresh", response_model=TokenResponse, summary="Access Token 갱신", description="쿠키의 Refresh Token을 사용하여 새 Access Token을 발급합니다.")
async def refresh_token(response: Response, request: Request, token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh Token으로 새 Access Token 발급"""
    refresh_token = token_refresh.refresh_token
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token이 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None

    user_id = AuthService.verify_refresh_token(db, refresh_token, client_ip, user_agent)
    if not user_id:
        response.delete_cookie(key="refresh_token", path="/auth/refresh")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 Refresh Token입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse, summary="내 정보 조회", description="현재 인증된 사용자의 정보를 조회합니다.")
async def get_current_user_info(current_user: Annotated[UserDTO, Depends(get_user_from_token)]):
    """현재 인증된 사용자 정보 조회"""
    return UserResponse(
        id=current_user.id,
        login_id=current_user.login_id,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
