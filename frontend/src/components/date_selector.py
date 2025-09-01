from datetime import datetime, timedelta
from typing import Tuple

import streamlit as st
from utils import get_date_now, get_date_now_minus_timedelta


def date_selector() -> Tuple[datetime, datetime]:
    """날짜 선택 컴포넌트를 렌더링하고 선택된 시작일과 종료일을 반환합니다.

    Returns:
        Tuple[datetime, datetime]: 선택된 시작일과 종료일
    """
    st.write("### 조회 기간 설정")

    # 세션 상태 초기화 (최초 실행 시에만)
    if "start_date_val" not in st.session_state:
        st.session_state.start_date_val = get_date_now_minus_timedelta(timedelta(days=30))
    if "end_date_val" not in st.session_state:
        st.session_state.end_date_val = get_date_now()

    # 콜백 함수: 날짜 입력 위젯 값이 변경될 때 세션 상태 업데이트
    def update_session_state_from_inputs():
        st.session_state.start_date_val = st.session_state.date_input_start
        st.session_state.end_date_val = st.session_state.date_input_end
        # 시작일이 종료일보다 늦으면 종료일을 시작일과 같게 조정
        if st.session_state.start_date_val > st.session_state.end_date_val:
            st.session_state.end_date_val = st.session_state.start_date_val

    col1, col2 = st.columns([3, 2])

    with col1:
        date_col1, date_col2 = st.columns(2)
        current_max_date = get_date_now()

        with date_col1:
            # st.date_input의 value를 세션 상태와 연결
            # key를 지정하여 세션 상태에서 해당 위젯의 값을 직접 참조 가능
            # on_change 콜백으로 세션 상태를 명시적으로 업데이트
            st.date_input(
                "시작일",
                value=st.session_state.start_date_val,
                max_value=current_max_date,  # 오늘까지로 제한
                key="date_input_start",  # 위젯의 현재 값을 st.session_state.date_input_start로 접근 가능
                on_change=update_session_state_from_inputs,
            )

        with date_col2:
            st.date_input(
                "종료일",
                value=st.session_state.end_date_val,
                max_value=current_max_date,  # 오늘까지로 제한
                key="date_input_end",
                on_change=update_session_state_from_inputs,
            )

    with col2:
        # 날짜 선택 버튼
        st.write("빠른 기간 선택")
        col_buttons = st.columns(3)
        today = get_date_now()  # 버튼 클릭 시 종료일을 오늘로 설정하기 위함

        with col_buttons[0]:
            btn_1m = st.button("1개월", key="btn_1m", use_container_width=True)
            if btn_1m:
                st.session_state.start_date_val = today - timedelta(days=30)
                st.session_state.end_date_val = today
                st.rerun()

        with col_buttons[1]:
            btn_3m = st.button("3개월", key="btn_3m", use_container_width=True)
            if btn_3m:
                st.session_state.start_date_val = today - timedelta(days=90)
                st.session_state.end_date_val = today
                st.rerun()

        with col_buttons[2]:
            btn_6m = st.button("6개월", key="btn_6m", use_container_width=True)
            if btn_6m:
                st.session_state.start_date_val = today - timedelta(days=180)
                st.session_state.end_date_val = today
                st.rerun()

    # 세션 상태에 저장된 date 객체를 datetime 객체로 변환하여 반환
    # st.date_input은 date 객체를 반환하므로, 이를 사용합니다.
    start_datetime = datetime.combine(st.session_state.start_date_val, datetime.min.time())
    end_datetime = datetime.combine(st.session_state.end_date_val, datetime.max.time())

    return start_datetime, end_datetime
