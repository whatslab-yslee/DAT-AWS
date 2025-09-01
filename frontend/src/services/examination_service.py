"""
환자 진단 관련 기능을 제공하는 모듈입니다.
진단 UI 렌더링, 진단 시작, 환자 진단 처리 등의 기능을 포함합니다.
"""

import time

from api_clients.diagnosis_client import get_diagnosis_client
from api_clients.schemas.diagnosis_schema import DiagnosisState
from api_clients.sse_client import get_sse_client
from components.vr_mock_renderer import redirect_to_vr_mock_client
from config import get_settings
from constants import Content
from services.patient_service import render_patient_dropdown_and_form
import streamlit as st


def render_patient_examination_ui() -> None:
    """환자 진단 UI를 렌더링합니다."""
    is_on_examination = st.session_state.get("on_examination", False)
    if is_on_examination:
        st.warning("진단 중에는 설정을 변경할 수 없습니다. 다시 시작하려면 진단 종료를 눌러 주세요.")

    # 환자 드롭다운 표시 및 환자 등록 폼 처리
    render_patient_dropdown_and_form()

    # 환자가 선택된 경우에만 진단 설정 표시
    if st.session_state.selected_patient:
        content_display_name = st.selectbox("콘텐츠 선택", Content.get_display_names(), disabled=is_on_examination)
        level = st.slider("난이도 선택", 1, 3, 1, disabled=is_on_examination)

        # 내부용 코드와 API용 코드를 모두 가져옵니다
        content_code = Content.get_code(content_display_name)
        content_api_code = Content.get_api_code(content_display_name)

        st.caption(Content.get_description(content_display_name))
        st.markdown("---")
        handle_examination_buttons(content_code, content_api_code, level)


def handle_examination_buttons(content: str, content_api_code: str, level: int) -> None:
    """진단 시작 버튼을 처리합니다.

    Args:
        content: 콘텐츠 코드
        content_api_code: API용 콘텐츠 코드
        level: 난이도
    """
    col1, col2 = st.columns(2)
    with col1:
        startExamination_button = st.button("진단 시작")
    with col2:
        endExamination_button = st.button("진단 종료")

    if startExamination_button:
        handle_start_examination(content, content_api_code, level)
    if endExamination_button:
        handle_end_examination()

    # # VR 모킹 버튼 표시 및 처리
    st.markdown("---")
    redirect_to_vr_mock_client()


def handle_end_examination() -> None:
    """진단을 종료합니다."""
    diagnosis_client = get_diagnosis_client()
    diagnosis_client.set_token(st.session_state.access_token)
    diagnosis_client.cancel_diagnosis(st.session_state.diagnosis_id)
    st.session_state.on_examination = False
    st.session_state.diagnosis_id = None
    st.rerun()


def handle_start_examination(content: str, content_api_code: str, level: int) -> None:
    """진단을 시작합니다.

    Args:
        content: 콘텐츠 코드
        content_api_code: API용 콘텐츠 코드
        level: 난이도
    """
    # 세션 상태 저장
    st.session_state.content = content
    st.session_state.level = level

    # 시작 시간 저장
    st.session_state.start_time = time.time()
    # 완료 시간 초기화
    if "completion_time" in st.session_state:
        del st.session_state.completion_time

    # 인증 확인 (안전하게 세션 변수 접근)
    is_logged_in = "is_logged_in" in st.session_state and st.session_state.is_logged_in
    has_token = "access_token" in st.session_state and st.session_state.access_token

    if not is_logged_in or not has_token:
        st.error("로그인이 필요합니다.")
        return

    # 진단 클라이언트 초기화 및 토큰 설정
    diagnosis_client = get_diagnosis_client()
    diagnosis_client.set_token(st.session_state.access_token)

    # 1. 라이브 세션 확인
    live_response = diagnosis_client.get_live_diagnosis()
    if live_response.success and live_response.data:
        st.info("정상적으로 종료되지 않은 진단이 확인되었습니다.")
        # 2. 라이브 세션이 있으면 실패 처리
        fail_response = diagnosis_client.cancel_diagnosis(live_response.data.id)
        if fail_response.success:
            st.success("이전 진단을 종료하고 새 진단을 시작합니다.")
        else:
            st.warning(f"이전 진단 세션 실패 처리에 실패했습니다: {fail_response.error or '알 수 없는 오류'}. 새 진단을 계속 진행합니다.")
    elif live_response.error and "404" not in str(live_response.error):  # 404는 라이브 세션이 없는 것이므로 정상
        st.info("새 진단을 시작합니다.")

    # 데이터 유효성 검사
    try:
        patient_id_int = int(st.session_state.selected_patient.id)
    except (ValueError, TypeError) as e:
        st.error(f"환자 ID가 올바르지 않습니다: {str(e)}")
        return

    # API용 콘텐츠 코드 검증
    if not content_api_code:
        st.error("콘텐츠 타입이 올바르지 않습니다")
        return

    # 3. 새 진단 시작 API 호출
    with st.spinner("진단 세션을 시작하는 중..."):
        response = diagnosis_client.start_diagnosis(patient_id=patient_id_int, diagnosis_type=content_api_code, level=level)

    if response.success and response.data:
        # 진단 ID 저장
        st.session_state.diagnosis_id = response.data.id
        st.session_state.diagnosis_code = response.data.code
        st.session_state.diagnosis_expired_at = response.data.expired_at
        st.session_state.diagnosis_state = DiagnosisState.READY.value

        # 사용자 결과 리포트 화면으로 이동하기 위해 플래그 설정
        st.session_state.on_examination = True

        # SSE 클라이언트를 사용하여 모니터링 시작
        sse_client = get_sse_client()
        settings = get_settings()
        endpoint_url = f"{settings.API_BASE_URL}/diagnosis/{st.session_state.diagnosis_id}/status"
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

        success = sse_client.start_sse_connection(endpoint_url, headers)
        if not success:
            st.error("SSE 연결이 실패했습니다.")
    else:
        error_message = response.error if response.error else "진단 시작에 실패했습니다."
        st.error(error_message)
