"""
VR 클라이언트 모킹 UI 관련 기능을 제공하는 모듈입니다.
진단 세션 입장 및 결과 업로드 버튼 등의 UI 기능을 포함합니다.
"""

from api_clients.vr_mock_client import get_vr_mock_client
from config import get_settings
import streamlit as st


# VR 모킹 관련 세션 상태 키
VR_DIAGNOSIS_ID_KEY = "vr_diagnosis_id"


def redirect_to_vr_mock_client() -> None:
    """VR 클라이언트 모킹 페이지로 리다이렉트합니다."""
    base_url = "http://localhost:8000" if get_settings().is_local else "https://dat-temp.whatslab.co.kr"
    st.link_button(
        label="VR 클라이언트 모킹 페이지 열기",
        url=f"{base_url}/api/test/mock-vr",
        help="VR 클라이언트 모킹 페이지로 이동합니다.",
    )


def handle_vr_mock_controls() -> None:
    """VR 클라이언트 모킹을 위한 버튼만 표시하고 처리합니다.
    SSE 상태나 이벤트 목록을 직접 렌더링하지 않습니다.
    """
    # 세션 상태 초기화
    if VR_DIAGNOSIS_ID_KEY not in st.session_state:
        st.session_state[VR_DIAGNOSIS_ID_KEY] = None
    st.markdown("### VR 클라이언트 모킹")

    # 진단 코드 확인
    has_code = "diagnosis_code" in st.session_state and st.session_state.diagnosis_code

    # VR 클라이언트 세션 입장 버튼
    col1, col2 = st.columns(2)
    with col1:
        join_button = st.button(
            "진단 세션 입장",
            disabled=not has_code,
            help="VR 클라이언트가 진단 세션에 입장합니다. 진단 코드가 필요합니다.",
        )

    # VR 클라이언트 결과 업로드 버튼
    with col2:
        upload_button = st.button(
            "진단 결과 업로드", disabled=not st.session_state[VR_DIAGNOSIS_ID_KEY], help="VR 클라이언트가 진단 결과를 업로드합니다. 세션 입장이 필요합니다."
        )

    # 버튼 동작 처리
    if join_button and has_code:
        handle_vr_join(st.session_state.diagnosis_code)

    if upload_button and st.session_state[VR_DIAGNOSIS_ID_KEY]:
        handle_vr_upload(st.session_state[VR_DIAGNOSIS_ID_KEY])

    # 세션 상태 표시
    if st.session_state[VR_DIAGNOSIS_ID_KEY]:
        st.success(f"VR 세션 입장 완료: 세션 ID {st.session_state[VR_DIAGNOSIS_ID_KEY]}")


def handle_vr_join(code: str) -> None:
    """VR 클라이언트 진단 세션 입장을 처리합니다.

    Args:
        code: 진단 코드
    """
    vr_client = get_vr_mock_client()

    with st.spinner("진단 세션에 입장 중..."):
        response = vr_client.join_diagnosis(code)

    if response.success:
        # 세션 정보 저장
        data = response.data
        st.session_state[VR_DIAGNOSIS_ID_KEY] = data.id
        st.success("진단 세션 입장 성공!")
    else:
        st.error(f"진단 세션 입장 실패: {response.error}")


def handle_vr_upload(diagnosis_id: int) -> None:
    """VR 클라이언트 진단 결과 업로드를 처리합니다.

    Args:
        diagnosis_id: 진단 ID
    """
    vr_client = get_vr_mock_client()

    with st.spinner("진단 결과를 업로드 중..."):
        response = vr_client.upload_diagnosis_result(diagnosis_id)

    if response.success:
        st.success("진단 결과 업로드 성공!")
    else:
        st.error(f"진단 결과 업로드 실패: {response.error}")
