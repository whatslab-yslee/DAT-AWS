from collections import deque
import logging
import random
import string
from typing import Set


logger = logging.getLogger(__name__)


class DiagnosisPasswordManager:
    """
    진단 비밀번호 관리자
    - 중복 없는 비밀번호 생성
    - 현재 사용 중인 비밀번호 관리
    - 진단 완료 시 비밀번호 해제
    """

    # 기본 값 설정
    DEFAULT_POOL_SIZE = 1000
    DEFAULT_PASSWORD_LENGTH = 4

    def __init__(self, pool_size: int = DEFAULT_POOL_SIZE, password_length: int = DEFAULT_PASSWORD_LENGTH):
        """
        비밀번호 관리자 초기화

        Args:
            pool_size: 비밀번호 풀 크기 (기본값: 1000)
            password_length: 비밀번호 길이 (기본값: 4)
        """
        # 현재 사용 중인 비밀번호 집합
        self._active_passwords: Set[str] = set()

        # 사용 가능한 비밀번호 풀 (큐)
        self._available_passwords: deque = deque()

        # 비밀번호 풀 초기화
        self._initialize_password_pool(pool_size, password_length)

        logger.info(f"비밀번호 관리자 초기화 완료: 풀 크기={pool_size}, 비밀번호 길이={password_length}")

    def _initialize_password_pool(self, pool_size: int, password_length: int) -> None:
        """
        사용 가능한 비밀번호 풀을 초기화

        Args:
            pool_size: 생성할 비밀번호 풀 크기
            password_length: 비밀번호 길이
        """
        # 중복 없는 비밀번호 집합 생성
        generated_passwords = set()

        # 요청한 풀 크기만큼 비밀번호 생성
        while len(generated_passwords) < pool_size:
            password = "".join(random.choices(string.digits, k=password_length))
            generated_passwords.add(password)

        # 생성된 비밀번호를 큐에 추가
        self._available_passwords.extend(generated_passwords)

        logger.info(f"비밀번호 풀 초기화 완료: {pool_size}개 생성됨")

    def generate_password(self) -> str:
        """
        비밀번호 풀에서 사용 가능한 비밀번호를 가져옴

        Returns:
            생성된 비밀번호

        Raises:
            RuntimeError: 사용 가능한 비밀번호가 없는 경우
        """
        # 사용 가능한 비밀번호가 없는 경우 예외 발생
        if not self._available_passwords:
            logger.error("사용 가능한 비밀번호가 없습니다. 모든 비밀번호가 사용 중입니다.")
            raise RuntimeError("사용 가능한 비밀번호가 없습니다. 모든 비밀번호가 사용 중입니다.")

        # 풀에서 비밀번호 하나 가져오기
        password = self._available_passwords.popleft()

        # 활성 비밀번호 집합에 추가
        self._active_passwords.add(password)

        logger.info(f"비밀번호 할당: {password}, 남은 개수: {len(self._available_passwords)}")
        return password

    def release_password(self, password: str) -> None:
        """
        비밀번호 사용 해제 후 풀에 반환 (진단 완료 시 호출)

        Args:
            password: 해제할 비밀번호
        """
        if password in self._active_passwords:
            # 활성 목록에서 제거
            self._active_passwords.remove(password)
            # 사용 가능한 풀에 다시 추가
            self._available_passwords.append(password)
            logger.info(f"비밀번호 해제 및 풀 반환: {password}, 사용 가능 개수: {len(self._available_passwords)}")
        else:
            logger.warning(f"해제 요청된 비밀번호가 활성 상태가 아님: {password}")

    def is_password_active(self, password: str) -> bool:
        """
        비밀번호가 현재 활성 상태인지 확인

        Args:
            password: 확인할 비밀번호

        Returns:
            활성 상태 여부
        """
        return password in self._active_passwords

    def get_active_passwords_count(self) -> int:
        """
        현재 활성 상태인 비밀번호 개수 반환

        Returns:
            활성 비밀번호 개수
        """
        return len(self._active_passwords)

    def get_available_passwords_count(self) -> int:
        """
        현재 사용 가능한 비밀번호 개수 반환

        Returns:
            사용 가능한 비밀번호 개수
        """
        return len(self._available_passwords)
