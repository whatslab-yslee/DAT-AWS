import base64
import json
from typing import Optional

from .time import get_timestamp_now


def extract_expiry_from_token(token: str) -> int:
    """JWT 토큰에서 만료 시간(timestamp)을 추출"""
    try:
        # JWT 토큰의 페이로드 부분 추출
        payload = token.split(".")[1]

        # 페이로드 base64 디코딩
        padding_needed = len(payload) % 4
        if padding_needed:
            payload += "=" * (4 - padding_needed)

        decoded_payload = base64.b64decode(payload)
        token_data = json.loads(decoded_payload)

        if "exp" in token_data:
            return int(token_data["exp"])

        return get_timestamp_now()
    except (IndexError, json.JSONDecodeError, base64.binascii.Error) as e:
        print(f"토큰 파싱 오류: {str(e)}")
        return get_timestamp_now()


def decode_token_payload(token: str) -> Optional[dict]:
    """JWT 토큰의 페이로드를 디코딩합니다.

    Args:
        token: JWT 토큰

    Returns:
        Optional[dict]: 디코딩된 페이로드 데이터 또는 디코딩 실패시 None
    """
    try:
        # JWT 토큰의 페이로드 부분 추출
        payload = token.split(".")[1]

        # 페이로드 base64 디코딩
        padding_needed = len(payload) % 4
        if padding_needed:
            payload += "=" * (4 - padding_needed)

        decoded_payload = base64.b64decode(payload)
        return json.loads(decoded_payload)
    except (IndexError, json.JSONDecodeError, base64.binascii.Error) as e:
        print(f"토큰 파싱 오류: {str(e)}")
        return None
