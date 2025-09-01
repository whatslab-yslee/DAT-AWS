import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# .env 파일이 루트에 있으므로:
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


class Settings:
    def __init__(self):
        # 실행 환경 설정
        self.ENV = os.getenv("ENV", "production")  # ENV가 없으면 기본값은 'production'
        self.is_local = self.ENV == "local"

        # 데이터베이스 설정
        self.POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.POSTGRES_DB = os.getenv("POSTGRES_DB", "mydb")
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

        # S3 관련 설정
        self.S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "test-bucket")
        self.AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
        self.LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localstack:4566")

        # 토큰 및 보안
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))
        self.SECRET_KEY = os.getenv("SECRET_KEY", "my-secret-key")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ALLOW_MULTIPLE_SESSIONS = os.getenv("ALLOW_MULTIPLE_SESSIONS", "true").lower() == "true"
        self.ADMIN_CODE = os.getenv("ADMIN_CODE", "1234")

        # User-Agent 관련 설정
        self.VR_CLIENT_USER_AGENTS = get_list_from_env("VR_CLIENT_USER_AGENTS")


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def get_list_from_env(var_name: str, default: List[str] = None) -> List[str]:
    """환경 변수에서 쉼표로 구분된 문자열 목록을 가져옵니다."""
    env_value = os.getenv(var_name)
    if not env_value:
        return default or []
    return [item.strip() for item in env_value.split(",")]


settings = Settings()
