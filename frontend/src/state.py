"""
세션 상태 관리 관련 기능을 제공하는 모듈입니다.
세션 변수 초기화, 세션 상태 관리 등의 기능을 포함합니다.
"""

import queue

from api_clients.auth_client import get_auth_client
from constants import Content
from services.auth_service import init_auth_states
import streamlit as st


def init_all_states() -> None:
    """전체 세션 상태 초기화"""
    _init_content_states()
    _init_diagnosis_states()
    _init_sse_states()
    _init_time_states()

    auth_client = get_auth_client()
    init_auth_states(auth_client=auth_client)


def _init_content_states() -> None:
    """콘텐츠 및 진단 설정 관련 세션 변수 초기화"""
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    if "content" not in st.session_state:
        st.session_state.content = Content.BALANCEBALL.value.code
    if "level" not in st.session_state:
        st.session_state.level = 1


def _init_diagnosis_states() -> None:
    """진단 상태 관련 세션 변수 초기화"""
    if "on_examination" not in st.session_state:
        st.session_state.on_examination = False
    if "diagnosis_id" not in st.session_state:
        st.session_state.diagnosis_id = None


def _init_sse_states() -> None:
    """SSE 관련 세션 변수 초기화"""
    if "sse_queue" not in st.session_state:
        st.session_state.sse_queue = queue.Queue()
    if "sse_events" not in st.session_state:
        st.session_state.sse_events = []
    if "sse_connected" not in st.session_state:
        st.session_state.sse_connected = False
    if "sse_error" not in st.session_state:
        st.session_state.sse_error = None


def _init_time_states() -> None:
    """세션 시간 관련 세션 변수 초기화"""
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "completion_time" not in st.session_state:
        st.session_state.completion_time = None
    if "expired_time" not in st.session_state:
        st.session_state.expired_time = None
