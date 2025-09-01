from components.graphic import local_css
from components.sidebar_navigation import sidebar_navigation
from constants import LOGO_WIDTH, MAIN_CSS_PATH, WHATSLAB_LOGO_URL, WONJU_LOGO_URL, YENSEI_ICON_URL
from services.patient_service import render_patient_registration_form, render_patients_table
import streamlit as st


def main_page():
    st.write("# 환자 관리")
    render_patient_registration_form()
    render_patients_table()


def side_bar():
    sidebar_navigation()
    with st.sidebar:
        st.image(WONJU_LOGO_URL, use_container_width=True)
        st.write("---")
        st.image(WHATSLAB_LOGO_URL, use_container_width=False, width=LOGO_WIDTH)


if __name__ == "__main__":
    st.set_page_config(page_title="환자 관리", page_icon=YENSEI_ICON_URL, layout="wide")

    if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
        st.switch_page("main.py")

    local_css(MAIN_CSS_PATH)
    side_bar()
    main_page()
