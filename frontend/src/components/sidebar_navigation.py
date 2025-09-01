from components.graphic import local_css
from constants import NAVIGATION_CSS_PATH
import streamlit as st


def sidebar_navigation():
    local_css(NAVIGATION_CSS_PATH)

    with st.sidebar:
        st.page_link("main.py", label="메인페이지", icon="🏠")
        st.page_link("pages/1_tutorial.py", label="사용 가이드", icon="📕")
        st.page_link("pages/2_database.py", label="데이터베이스", icon="💾")
        st.page_link("pages/3_patient.py", label="환자 관리", icon="👩‍⚕️")
