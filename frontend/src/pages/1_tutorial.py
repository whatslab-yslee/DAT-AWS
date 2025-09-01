from components.graphic import local_css
from components.sidebar_navigation import sidebar_navigation
from constants import LOGO_WIDTH, MAIN_CSS_PATH, TUTORIAL_DESCRIPTION, TUTORIAL_PDF_URL, TUTORIAL_VIDEO_URL, WHATSLAB_LOGO_URL, WONJU_LOGO_URL, YENSEI_ICON_URL
import streamlit as st


def tutorial_video():
    st.video(TUTORIAL_VIDEO_URL)


def side_bar():
    sidebar_navigation()
    with st.sidebar:
        st.image(WONJU_LOGO_URL, use_container_width=True)
        st.caption(TUTORIAL_DESCRIPTION)
        st.write("---")
        st.image(WHATSLAB_LOGO_URL, use_container_width=False, width=LOGO_WIDTH)


def main_page():
    st.write("# 사용 가이드")

    st.caption("재활마을 영상으로 둘러보기")
    tutorial_video()

    st.caption("재활마을 문서로 확인하기")
    st.link_button("가이드 문서 열기", TUTORIAL_PDF_URL, use_container_width=False)


if __name__ == "__main__":
    st.set_page_config(page_title="사용 가이드", page_icon=YENSEI_ICON_URL, layout="wide")

    if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
        st.switch_page("main.py")

    local_css(MAIN_CSS_PATH)
    side_bar()

    main_page()
