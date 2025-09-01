from components.graphic import local_css
from components.sidebar_navigation import sidebar_navigation
from components.sse_renderer import render_diagnosis_results
from constants import LOGO_WIDTH, MAIN_CSS_PATH, MAIN_HEADER_CSS_PATH, WHATSLAB_LOGO_URL, WONJU_LOGO_URL, YENSEI_ICON_URL
from services.auth_service import render_login_ui, render_logout_ui
from services.examination_service import render_patient_examination_ui
from state import init_all_states
import streamlit as st


def main():
    st.set_page_config(page_title="메인페이지", page_icon=YENSEI_ICON_URL, layout="wide")

    # 세션 상태 초기화
    init_all_states()

    # CSS 로드
    local_css(MAIN_CSS_PATH)

    # 로그인 상태에 따라 사이드바 페이지 내비게이션 숨김 처리
    if "is_logged_in" in st.session_state and st.session_state.is_logged_in:
        sidebar_navigation()

    # UI 구성 요소 렌더링
    side_bar()
    main_page()


def main_page() -> None:
    """메인 페이지를 렌더링합니다."""
    header_container = st.container()
    with header_container:
        local_css(MAIN_HEADER_CSS_PATH)
        st.write("# 재활마을")
        st.write("#### 가상현실 기반 디지털 치료 서비스")
        st.write("---")

    if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
        st.warning("로그인이 필요합니다. 회원가입은 관리자에게 문의하세요.")
        return

    on_examination = "on_examination" in st.session_state and st.session_state.on_examination
    has_diagnosis_id = "diagnosis_id" in st.session_state and st.session_state.diagnosis_id

    # 진단 상태에 따른 컨텐츠 표시
    if on_examination and has_diagnosis_id:
        render_diagnosis_results()
    else:
        st.error("진단 시작 버튼을 눌러 진단을 진행해주세요.")


def side_bar() -> None:
    """사이드바를 렌더링합니다."""
    with st.sidebar:
        st.image(WONJU_LOGO_URL, use_container_width=True)

        # 로그인 상태에 따른 사이드바 렌더링
        is_logged_in = "is_logged_in" in st.session_state and st.session_state.is_logged_in

        if not is_logged_in:
            render_login_ui()
        else:
            render_logout_ui()
            st.markdown("---")
            render_patient_examination_ui()
            st.markdown("---")

        st.image(WHATSLAB_LOGO_URL, use_container_width=False, width=LOGO_WIDTH)


if __name__ == "__main__":
    main()
