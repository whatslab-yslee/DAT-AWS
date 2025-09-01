from typing import List, Optional

from app.models.token import Token
from sqlalchemy.orm import Session


class TokenRepository:
    @staticmethod
    def delete_all_tokens_for_user(db: Session, user_id: int) -> bool:
        """사용자의 모든 리프레시 토큰 삭제"""
        db.query(Token).filter(Token.user_id == user_id).delete(synchronize_session=False)
        db.commit()
        return True

    @staticmethod
    def delete_tokens_from_other_ip(db: Session, user_id: int, current_ip: str) -> bool:
        """현재 IP를 제외한 다른 모든 IP의 리프레시 토큰 삭제"""
        db.query(Token).filter(Token.user_id == user_id, Token.ip_address != current_ip).delete(synchronize_session=False)
        db.commit()
        return True

    @staticmethod
    def find_token(db: Session, token: str) -> Optional[Token]:
        """리프레시 토큰 찾기"""
        return db.query(Token).filter(Token.refresh_token == token).first()

    @staticmethod
    def get_active_sessions(db: Session, user_id: int) -> List[Token]:
        """사용자의 활성 세션 목록 조회"""
        return db.query(Token).filter(Token.user_id == user_id).all()

    @staticmethod
    def create_token(db: Session, refresh_token: str, user_id: int, ip_address: str = None, user_agent: str = None) -> Token:
        """새 리프레시 토큰 생성"""
        new_token = Token(refresh_token=refresh_token, user_id=user_id, ip_address=ip_address, user_agent=user_agent)
        db.add(new_token)
        db.commit()
        return new_token

    @staticmethod
    def delete_token(db: Session, refresh_token: str) -> bool:
        """특정 리프레시 토큰 삭제"""
        result = db.query(Token).filter(Token.refresh_token == refresh_token).delete(synchronize_session=False)
        db.commit()
        return result > 0

    @staticmethod
    def delete_token_by_id(db: Session, token_id: int, user_id: int) -> bool:
        """특정 ID의 리프레시 토큰 삭제"""
        result = db.query(Token).filter(Token.id == token_id, Token.user_id == user_id).delete(synchronize_session=False)
        db.commit()
        return result > 0
