import os
import sys


# 이 스크립트가 있는 디렉토리의 부모 디렉토리(backend)를 sys.path에 추가합니다.
# 이렇게 하면 'app' 모듈을 정상적으로 임포트할 수 있습니다.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLAlchemy Base가 모델을 인식할 수 있도록 모든 모델을 임포트합니다.
# 이 과정이 없으면 Base.metadata가 비어있어 ERD가 생성되지 않습니다.
from app.configs.database import Base
from app.models import diagnosis, doctor, patient, token, user  # noqa: F401
from eralchemy import render_er


def draw_erd():
    """
    SQLAlchemy Base metadata를 기반으로 ERD(Entity-Relationship Diagram)를 생성합니다.

    실행 전 필요한 라이브러리를 설치해야 합니다:
    pip install eralchemy pygraphviz
    """
    # ERD를 저장할 경로 설정 (현재 스크립트와 동일한 디렉토리)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erd.png")

    print(f"ERD를 생성합니다. 저장 위치: {output_path}")

    try:
        # eralchemy2를 사용하여 ERD 렌더링
        render_er(Base, output_path)
        print(f"ERD 생성이 완료되었습니다. '{output_path}' 파일을 확인하세요.")
    except Exception as e:
        print(f"ERD 생성 중 오류가 발생했습니다: {e}")
        print("Graphviz가 시스템에 설치되어 있는지 확인해주세요.")


if __name__ == "__main__":
    draw_erd()
