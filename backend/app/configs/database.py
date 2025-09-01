from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .env_configs import get_settings


settings = get_settings()

# ORM BASE MODEL CLASS
Base = declarative_base()


# postgresql://username:password@host:port/dbname
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


engine = create_engine(DATABASE_URL, echo=settings.is_local, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
