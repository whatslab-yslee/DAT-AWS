"""
SSE 이벤트 처리 및 렌더링 관련 기능을 제공하는 모듈입니다.
진단 상태 표시, 이벤트 목록 표시, 모니터링 제어 등의 기능을 포함합니다.
"""

import time
from typing import Any, Dict, List, Tuple

from api_clients.diagnosis_client import get_diagnosis_client
from api_clients.sse_client import get_sse_client
from components.timer import client_side_timer
from config import get_settings
import streamlit as st
from utils import get_datetime_now, get_total_seconds_between_datetimes


# 이벤트 업데이트 간격 (초)
EVENT_UPDATE_INTERVAL = 5


def get_diagnosis_status() -> Tuple[Any, List[Dict], str]:
    """SSE 클라이언트를 초기화하고 현재 진단 상태를 가져옵니다.

    Returns:
        Tuple[Any, List[Dict], str]: SSE 클라이언트, 이벤트 목록, 현재 상태
    """
    sse_client = get_sse_client()

    # 큐 처리를 바로 수행하여 최신 이벤트 가져오기
    sse_client._process_queue()
    events = sse_client.get_events()

    # 진단 상태 확인
    current_state = "상태 정보 없음"
    if events:
        last_event = events[-1]
        current_state = last_event.get("state", "상태 정보 없음")

        # session_state 업데이트
        st.session_state.diagnosis_state = current_state

        if current_state in ["COMPLETED", "FINISHED"]:
            # 완료 시간이 없으면 현재 시간으로 설정
            if "completion_time" not in st.session_state:
                st.session_state.completion_time = time.time()

    return sse_client, events, current_state


def display_diagnosis_info() -> None:
    """진단 정보를 표시합니다."""
    with st.expander("진단 정보", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("환자 이름", st.session_state.selected_patient.name)
            # 콘텐츠 정보 추가
            if "content" in st.session_state:
                st.metric("콘텐츠", st.session_state.content)
        with col2:
            # if "diagnosis_code" in st.session_state:
            #     st.metric("진단 코드", st.session_state.diagnosis_code)
            st.metric("환자 코드", st.session_state.selected_patient.code)
            st.metric("난이도", st.session_state.level)
        with col3:
            # 세션 만료 시간 표시
            if "diagnosis_expired_at" in st.session_state:
                expired_at = st.session_state.diagnosis_expired_at
                st.metric("진단 종료 시간", expired_at.strftime("%H:%M:%S"))
            if "diagnosis_state" in st.session_state:
                st.metric("진단 현재 상태", st.session_state.diagnosis_state)


def handle_monitoring_controls(sse_client: Any) -> None:
    """모니터링 시작/중지 버튼을 표시하고 처리합니다.

    Args:
        sse_client: SSE 클라이언트 객체
    """
    # SSE 연결 상태에 따라 버튼 활성화/비활성화 설정
    is_connected = sse_client.is_connected()

    col1, col2 = st.columns(2)
    with col1:
        start_monitoring = st.button("모니터링 시작", disabled=is_connected)
    with col2:
        stop_monitoring = st.button("모니터링 중지", disabled=not is_connected)

    if start_monitoring:
        start_sse_monitoring(sse_client)

    if stop_monitoring:
        stop_sse_monitoring(sse_client)


def start_sse_monitoring(sse_client: Any) -> None:
    """SSE 모니터링을 시작합니다.

    Args:
        sse_client: SSE 클라이언트 객체
    """
    if not sse_client.is_connected():
        try:
            # 인증 확인
            if not st.session_state.is_logged_in or not st.session_state.access_token:
                st.error("로그인이 필요합니다.")
                return

            # 진단 클라이언트 초기화
            diagnosis_client = get_diagnosis_client()
            diagnosis_client.set_token(st.session_state.access_token)

            # 진단 상태 API 엔드포인트 URL 구성
            settings = get_settings()
            endpoint_url = f"{settings.API_BASE_URL}/diagnosis/{st.session_state.diagnosis_id}/status"

            # 헤더에 인증 토큰 추가
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

            # SSE 연결 시작
            success = sse_client.start_sse_connection(endpoint_url, headers)
            if not success:
                st.warning("진단 상태 모니터링 시작에 실패했습니다.")
        except Exception as e:
            st.error(f"모니터링 시작 중 오류가 발생했습니다: {str(e)}")
    else:
        st.info("이미 모니터링 중입니다.")


def stop_sse_monitoring(sse_client: Any) -> None:
    """SSE 모니터링을 중지합니다.

    Args:
        sse_client: SSE 클라이언트 객체
    """
    if sse_client.is_connected():
        success = sse_client.stop_sse_connection()
        if success:
            st.success("진단 모니터링이 중지되었습니다.")
        else:
            st.warning("진단 모니터링 중지에 실패했습니다.")
    else:
        st.info("활성화된 모니터링이 없습니다.")


def _handle_completed_state(sse_client: Any, current_state: str) -> None:
    """완료된 진단 상태를 처리합니다.

    Args:
        sse_client: SSE 클라이언트 객체
        current_state: 현재 진단 상태
    """
    st.success(f"진단이 완료되었습니다. 현재 상태: {current_state}")

    # 완료 상태인 경우 SSE 연결 종료
    if sse_client.is_connected():
        success = sse_client.stop_sse_connection()
        if success:
            st.info("모니터링이 종료되었습니다. 데이터베이스에서 진단 결과를 확인하세요.")


def _handle_failed_state(sse_client: Any, current_state: str) -> None:
    """실패한 진단 상태를 처리합니다.

    Args:
        sse_client: SSE 클라이언트 객체
        current_state: 현재 진단 상태
    """
    if current_state != "EXPIRED":
        st.error(f"진단이 종료되었습니다. 상태: {current_state}")

    # 비정상 종료 상태인 경우에도 SSE 연결 종료
    if sse_client.is_connected():
        success = sse_client.stop_sse_connection()
        if success:
            st.info("진단이 종료되어 모니터링이 자동 종료되었습니다.")


def display_status_info(sse_client: Any, current_state: str) -> None:
    """진단 상태 정보를 표시합니다.

    Args:
        sse_client: SSE 클라이언트 객체
        current_state: 현재 진단 상태
    """
    status_container = st.container()

    with status_container:
        if "diagnosis_expired_at" in st.session_state and current_state in ["READY", "STARTED", "EXPIRED"]:
            total_seconds = get_total_seconds_between_datetimes(get_datetime_now(), st.session_state.diagnosis_expired_at)
            client_side_timer(total_seconds=total_seconds, key="monitoring")

        # 에러 메시지 표시
        error = sse_client.get_error()
        if error:
            st.error(f"오류: {error}")

        # 연결 상태 표시
        if sse_client.is_connected():
            # 상태에 따른 메시지 표시
            if current_state in ["COMPLETED", "FINISHED"]:
                _handle_completed_state(sse_client, current_state)
            elif current_state in ["FAILED", "ERROR", "CANCELLED", "EXPIRED"]:
                _handle_failed_state(sse_client, current_state)
            else:
                st.info(f"진단 세션 현재 상태: {current_state}")
        else:
            if "diagnosis_id" in st.session_state and st.session_state.diagnosis_id:
                st.warning("진단 모니터링이 중지되었습니다. '모니터링 시작' 버튼을 클릭하여 재시작하세요.")


def display_events_list(events: List[Dict]) -> None:
    """이벤트 목록을 표시합니다.

    Args:
        events: 이벤트 목록
    """
    events_container = st.container()

    with events_container:
        st.subheader("이벤트 목록")

        # 상태별 이벤트 데이터프레임 생성 (중복 제거)
        if events:
            import pandas as pd

            # 중복 제거된 상태별 최신 이벤트만 보여주기
            unique_states = {}
            for event in events:
                state = event.get("state", "unknown")
                # 각 상태의 가장 최신 이벤트를 유지
                unique_states[state] = event

            deduped_events = list(unique_states.values())

            # 데이터프레임 변환
            events_df_data = {"시간": [], "이벤트 타입": [], "상태": [], "메시지": []}
            for event in deduped_events:
                # event가 딕셔너리인지 확인
                if isinstance(event, dict):
                    events_df_data["시간"].append(event.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")))
                    events_df_data["이벤트 타입"].append(event.get("event", "message"))
                    events_df_data["상태"].append(event.get("state", "-"))
                    events_df_data["메시지"].append(str(event.get("data", event)))
                else:
                    # 딕셔너리가 아닌 경우 (예: 단순 문자열) 처리
                    events_df_data["시간"].append(time.strftime("%Y-%m-%d %H:%M:%S"))
                    events_df_data["이벤트 타입"].append("unknown")
                    events_df_data["상태"].append("-")
                    events_df_data["메시지"].append(str(event))

            # 상태별로 정렬
            try:
                df = pd.DataFrame(events_df_data)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"데이터프레임 생성 오류: {e}")
        else:
            st.info("수신된 이벤트가 없습니다.")


def handle_periodic_refresh(sse_client: Any) -> None:
    """SSE 연결이 활성화된 경우 주기적으로 화면을 갱신합니다.

    Args:
        sse_client: SSE 클라이언트 객체
    """
    if sse_client.is_connected():
        time.sleep(EVENT_UPDATE_INTERVAL)
        st.rerun()


def render_diagnosis_results() -> None:
    """진단 결과 및 SSE 상태를 렌더링합니다."""
    st.subheader("진단 실시간 상태")

    # SSE 클라이언트 초기화 및 이벤트 처리
    sse_client, events, current_state = get_diagnosis_status()

    # 진단 정보 표시
    display_diagnosis_info()

    # 상태 정보 표시 - 먼저 실행하여 완료 상태인 경우 SSE 연결을 종료
    display_status_info(sse_client, current_state)

    # 모니터링 제어 버튼 표시 및 처리 - SSE 상태가 변경된 후 버튼 상태 결정
    handle_monitoring_controls(sse_client)

    # 이벤트 목록 표시
    display_events_list(events)

    # 주기적으로 화면 갱신 (SSE 연결 활성화 시)
    handle_periodic_refresh(sse_client)
