import os
from typing import Final


# 기본 디렉토리 경로
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CSS_DIR = os.path.join(_BASE_DIR, "assets", "css")


# S3 경로, 현재는 임시로 github 에서 가져오도록 설정
S3_URL: Final[str] = "https://raw.githubusercontent.com/whats-lab/DAT-assets/refs/heads/main/assets/"
_IMG_DIR = os.path.join(S3_URL, "images")
_PDF_DIR = os.path.join(S3_URL, "pdfs")

# ENV 파일 경로
ENV_FILE_PATH: Final[str] = os.path.join(os.path.dirname(_BASE_DIR), ".env")

# CSS 파일 URL
MAIN_CSS_PATH: Final[str] = os.path.join(_CSS_DIR, "style.css")
NAVIGATION_CSS_PATH: Final[str] = os.path.join(_CSS_DIR, "navigation.css")
MAIN_HEADER_CSS_PATH: Final[str] = os.path.join(_CSS_DIR, "main_header.css")

# 이미지 파일 URL
WONJU_LOGO_URL: Final[str] = os.path.join(_IMG_DIR, "wonju_logo.png")
WHATSLAB_LOGO_URL: Final[str] = os.path.join(_IMG_DIR, "whatslab_logo.png")
YENSEI_ICON_URL: Final[str] = os.path.join(_IMG_DIR, "yonsei_logo.png")

# 튜토리얼 파일 URL
TUTORIAL_VIDEO_URL: Final[str] = "https://youtu.be/fVA5_BvNiVc"
TUTORIAL_PDF_URL: Final[str] = os.path.join(_PDF_DIR, "whatslab-dat-manual-ver010.pdf")
