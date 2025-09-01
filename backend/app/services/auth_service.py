from datetime import timedelta
from typing import Union

from app.configs.env_configs import get_settings
from app.dtos.user_dto import TokenPairDTO, UserDTO, UserLoginDTO, UserRegistrationInputDTO, UserRoleDTO
from app.models.user import User, UserRole
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.services.doctor_service import DoctorService
from app.utils import get_datetime_from_timestamp, get_datetime_now, get_datetime_now_plus_timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session


# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()

# TODO: JWT 관련 Util 함수로 분리하고 설정 주입
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)

    @staticmethod
    def authenticate_user(db: Session, login_input: UserLoginDTO) -> Union[UserDTO, None]:
        user = UserRepository.find_by_login_id(db, login_input.login_id)
        if not user:
            return None
        if not AuthService.verify_password(login_input.password, user.hashed_password):
            return None
        return UserDTO.from_model(user)

    @staticmethod
    def create_access_token(user_id: int) -> str:
        """액세스 토큰 생성"""
        expire = get_datetime_now_plus_timedelta(timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """리프레시 토큰 생성"""
        expire = get_datetime_now_plus_timedelta(timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
        to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_tokens(db: Session, user_id: int, ip_address: str = None, user_agent: str = None) -> TokenPairDTO:
        """액세스 토큰과 리프레시 토큰 생성"""
        access_token = AuthService.create_access_token(user_id)
        refresh_token = AuthService.create_refresh_token(user_id)

        if settings.ALLOW_MULTIPLE_SESSIONS:
            if ip_address:
                existing_tokens = TokenRepository.get_active_sessions(db, user_id)
                for token in existing_tokens:
                    if token.ip_address == ip_address:
                        TokenRepository.delete_token(db, token.refresh_token)
        else:
            TokenRepository.delete_all_tokens_for_user(db, user_id)

        TokenRepository.create_token(db, refresh_token, user_id, ip_address, user_agent)

        return TokenPairDTO(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def get_user_from_token(db: Session, token: str) -> Union[UserDTO, None]:
        """현재 인증된 사용자 정보 조회"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str = payload.get("sub")
            token_type = payload.get("type")
            exp = payload.get("exp")

            if not user_id_str or token_type != "access" or not exp:
                return None

            user_id = int(user_id_str)

            # 토큰 만료 확인
            if get_datetime_now() > get_datetime_from_timestamp(exp):
                return None

            # 사용자 정보 조회
            user = UserRepository.find_by_id(db, user_id)
            if user is None:
                return None

            return UserDTO.from_model(user)
        except JWTError:
            return None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def verify_refresh_token(db: Session, refresh_token: str, ip_address: str = None, user_agent: str = None) -> Union[int, None]:
        """리프레시 토큰 검증 및 사용자 ID 반환"""
        try:
            # 토큰 디코딩 및 기본 검증
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))

            # 데이터베이스에서 토큰 검증
            token_record = TokenRepository.find_token(db, refresh_token)

            if not token_record:
                return None

            # IP 주소 검증
            if ip_address and token_record.ip_address and token_record.ip_address != ip_address:
                # IP가 변경된 경우 토큰 삭제
                TokenRepository.delete_token(db, refresh_token)
                return None

            # 사용자 에이전트 검증
            if user_agent and token_record.user_agent and token_record.user_agent != user_agent:
                # 사용자 에이전트가 변경된 경우 토큰 삭제
                TokenRepository.delete_token(db, refresh_token)
                return None

            # 타입 및 만료 검증
            token_type = payload.get("type")
            exp = payload.get("exp")
            if token_type != "refresh" or not exp:
                return None

            # 토큰 만료 검증
            if get_datetime_now() > get_datetime_from_timestamp(exp):
                TokenRepository.delete_token(db, refresh_token)
                return None

            # 사용자 확인
            user = UserRepository.find_by_id(db, user_id)
            if user is None or user.is_deleted:
                return None

            return user_id
        except Exception:
            return None

    @staticmethod
    def logout_user(db: Session, user_id: int) -> bool:
        """사용자 로그아웃 처리"""
        return TokenRepository.delete_all_tokens_for_user(db, user_id)

    @staticmethod
    def register_user(db: Session, registration_data: UserRegistrationInputDTO) -> UserDTO:
        """사용자 등록"""
        if registration_data.admin_code != settings.ADMIN_CODE:
            raise ValueError("관리자 코드가 일치하지 않습니다")

        if UserRepository.find_by_login_id(db, registration_data.login_id):
            raise ValueError("이미 사용 중인 로그인 ID입니다")

        # 비밀번호 해싱
        hashed_password = AuthService.get_password_hash(registration_data.password)

        # 사용자 생성
        new_user = User(
            login_id=registration_data.login_id,
            hashed_password=hashed_password,
            name=registration_data.name,
            role=UserRole(registration_data.role.value),
        )

        # 사용자 저장
        created_user = UserRepository.create(db, new_user)  # 이제 User 객체 전달

        try:
            if registration_data.role == UserRoleDTO.DOCTOR:
                DoctorService.create_doctor(db, created_user.id)
            elif registration_data.role == UserRoleDTO.PATIENT:
                raise ValueError("환자 단독 가입 불가")

        except Exception as e:
            print(f"Error during post-registration task for user {created_user.id}: {e}")
            raise RuntimeError("사용자 프로필 생성 중 오류가 발생했습니다.")

        return UserDTO.from_model(created_user)
