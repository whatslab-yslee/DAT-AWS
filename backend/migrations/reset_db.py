import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlalchemy as sa
from alembic.config import Config
from alembic import command

from app.configs.env_configs import get_settings


# DB 환경 변수 설정
settings = get_settings()
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT

db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# alembic.ini 파일 경로 확인
ALEMBIC_INI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
if not os.path.exists(ALEMBIC_INI_PATH):
    print(f"FATAL ERROR: alembic.ini file not found at '{ALEMBIC_INI_PATH}'")
    sys.exit(1)
def reset_database():
    """
    데이터베이스를 완전히 초기화하는 메인 함수입니다.
    1. 개별 테이블/타입 삭제 -> 2. 스키마 전체 삭제 -> 3. Alembic 마이그레이션 순으로 진행합니다.
    """
    print("\n--- [START] 데이터베이스 초기화 스크립트 ---")

    engine = sa.create_engine(db_url, isolation_level="AUTOCOMMIT")

    # --- 단계 1: 개별 테이블 및 타입 삭제 (1차 정리) ---    
    print("\n[단계 1/3] 개별 테이블 및 타입을 삭제합니다...")

    TABLES_TO_DROP = [
        "diagnosis_results",
        "diagnosis_sessions",
        "diagnoses",
        "patients",
        "tokens",
        "doctors",
        "users",
        "alembic_version"  # Alembic 관리 테이블도 명시적으로 삭제
    ]
    ENUMS_TO_DROP = [
        "diagnosisstate",
        "diagnosistype",
        "userrole",
        "diagnosisresultfiletype"
    ]

    with engine.connect() as connection:
        try:
            # 모든 테이블 삭제
            for table in TABLES_TO_DROP:
                print(f"  -> 실행: DROP TABLE IF EXISTS \"{table}\" CASCADE;")
                connection.execute(sa.text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))

            # 모든 ENUM 타입 삭제
            for enum in ENUMS_TO_DROP:
                print(f"  -> 실행: DROP TYPE IF EXISTS {enum};")
                connection.execute(sa.text(f"DROP TYPE IF EXISTS {enum};"))

            print("  - 성공: 개별 테이블 및 타입 삭제가 완료되었습니다.")

        except Exception as e:
            print(f"\n[WARNING] 개별 객체 삭제 중 오류가 발생했지만 계속 진행합니다: {e}")

    # --- 단계 2: 스키마 리셋 (2차 정리) ---
    # 모든 객체를 한번에 삭제하는 가장 확실한 방법입니다.
    print("\n[단계 2/3] 'public' 스키마를 리셋합니다...")

    with engine.connect() as connection:
        try:
            print("  -> 실행: DROP SCHEMA public CASCADE;")
            connection.execute(sa.text("DROP SCHEMA public CASCADE;"))
            print("  - 성공: 'public' 스키마가 삭제되었습니다.")

            print("  -> 실행: CREATE SCHEMA public;")
            connection.execute(sa.text("CREATE SCHEMA public;"))
            print("  - 성공: 'public' 스키마가 생성되었습니다.")

            print("  -> 'public' 스키마에 기본 권한을 부여합니다...")
            connection.execute(sa.text(f"GRANT ALL ON SCHEMA public TO {POSTGRES_USER};"))
            connection.execute(sa.text("GRANT ALL ON SCHEMA public TO public;"))
            print("  - 성공: 권한이 부여되었습니다.")

        except Exception as e:
            print(f"\n[FATAL ERROR] 스키마 리셋 중 오류가 발생했습니다: {e}")
            print("\n스크립트를 중단합니다.")
            sys.exit(1)

    print("\n[성공] 스키마 리셋이 완료되었습니다.")

    # --- 단계 3: Alembic 마이그레이션 실행 ---
    # 깨끗해진 데이터베이스 위에 모든 마이그레이션을 적용하여 스키마를 구성합니다.
    print("\n[단계 3/3] 모든 Alembic 마이그레이션을 최신 버전으로 적용합니다...")
    try:
        alembic_cfg = Config(ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        command.upgrade(alembic_cfg, "head")
        print("\n[성공] Alembic 마이그레이션이 적용되었습니다. 데이터베이스가 최신 상태입니다.")
    except Exception as e:
        print(f"\n[FATAL ERROR] 'alembic upgrade' 중 오류가 발생했습니다: {e}")
        print("\n스크립트를 중단합니다.")
        sys.exit(1)

    print("\n--- [COMPLETE] 데이터베이스가 성공적으로 초기화되었습니다! ---")


if __name__ == "__main__":
    reset_database()
