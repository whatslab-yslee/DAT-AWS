from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context


# models import
from app.configs.database import Base
from app.models import diagnosis, doctor, patient, user, token

# or if you have multiple, from app.models import user, other_model
# then Base = user.Base

from app.configs.env_configs import get_settings

# Alembic Config
config = context.config

# DB 관련 환경 변수 가져오기
settings = get_settings()
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT

db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# alembic.ini에 명시된 url을 동적으로 덮어씌우기
config.set_main_option("sqlalchemy.url", db_url)

# Logging 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 타겟 메타데이터 (모든 모델의 Base)
target_metadata = Base.metadata

def run_migrations_offline():
    """Offline mode"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Online mode"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
