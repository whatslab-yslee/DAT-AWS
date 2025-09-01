from typing import Union

from app.models.user import User
from sqlalchemy.orm import Session


class UserRepository:
    @staticmethod
    def find_by_login_id(db: Session, login_id: str) -> Union[User, None]:
        return db.query(User).filter(User.login_id == login_id, User.is_deleted.is_(False)).first()

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def find_by_id(db: Session, user_id: int) -> Union[User, None]:
        return db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()

    @staticmethod
    def update(db: Session, user: User, updates: dict) -> User:
        """사용자 정보 업데이트"""
        for key, value in updates.items():
            if hasattr(user, key) and key != "id" and key != "hashed_password":
                setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_password(db: Session, user: User, hashed_password: str) -> User:
        """사용자 비밀번호 업데이트"""
        user.hashed_password = hashed_password
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> bool:
        """사용자 삭제"""
        user.is_deleted = True
        db.commit()
        return True
