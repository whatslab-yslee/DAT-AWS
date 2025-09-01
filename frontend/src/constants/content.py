from dataclasses import dataclass
from enum import Enum
from typing import Optional

from constants.text import BALANCEBALL_DESCRIPTION, FITBOX_DESCRIPTION, TENNISBALL_DESCRIPTION


@dataclass
class ContentInfo:
    display_name: str  # 표시용 이름 (한글)
    code: str  # 시스템 내부에서 사용하는 코드 (영문)
    api_code: str  # API 호출 시 사용하는 코드 (대문자)
    description: str  # 콘텐츠에 대한 설명


class Content(Enum):
    BALANCEBALL = ContentInfo(display_name="밸런스볼 (BalanceBall)", code="BalanceBall", api_code="BALANCEBALL", description=BALANCEBALL_DESCRIPTION)
    FITBOX = ContentInfo(display_name="피트박스 (FitBox)", code="FitBox", api_code="FITBOX", description=FITBOX_DESCRIPTION)
    TENNISBALL = ContentInfo(display_name="테니스볼 (TennisBall)", code="TennisBall", api_code="TENNISBALL", description=TENNISBALL_DESCRIPTION)

    @classmethod
    def get_display_names(cls) -> list[str]:
        return [content.value.display_name for content in cls]

    @classmethod
    def from_display_name(cls, display_name: str) -> Optional["Content"]:
        for content in cls:
            if content.value.display_name == display_name:
                return content
        return None

    @classmethod
    def get_code(cls, display_name: str) -> Optional[str]:
        content = cls.from_display_name(display_name)
        return content.value.code if content else None

    @classmethod
    def get_api_code(cls, display_name: str) -> Optional[str]:
        """API 호출 시 사용할 콘텐츠 코드(대문자)를 반환합니다."""
        content = cls.from_display_name(display_name)
        return content.value.api_code if content else None

    @classmethod
    def get_description(cls, display_name: str) -> Optional[str]:
        content = cls.from_display_name(display_name)
        return content.value.description if content else None
