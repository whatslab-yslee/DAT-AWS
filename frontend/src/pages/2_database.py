from datetime import datetime

from api_clients.diagnosis_record_client import get_diagnosis_record_client
from components.date_selector import date_selector
from components.graphic import local_css, report
from components.sidebar_navigation import sidebar_navigation
from constants import DATABASE_DESCRIPTION, LOGO_WIDTH, MAIN_CSS_PATH, WHATSLAB_LOGO_URL, WONJU_LOGO_URL, YENSEI_ICON_URL
from services.patient_service import render_patient_dropdown_and_form
import streamlit as st


def format_datetime(dt: datetime) -> str:
    """날짜 시간을 보기 좋은 형식으로 변환합니다."""
    return dt.strftime("%Y년 %m월 %d일 %H:%M")


def get_diagnosis_type_display(type_code: str) -> str:
    """진단 타입 코드를 한글 표시로 변환합니다."""
    type_map = {"TENNISBALL": "테니스 볼", "BALANCEBALL": "밸런스 볼", "FITBOX": "피트박스"}
    return type_map.get(type_code, type_code)


def render_diagnosis_record_detail(diagnosis_id: int):
    """선택된 진단 기록의 상세 정보를 표시합니다."""
    if not diagnosis_id:
        return

    # 진단 기록 클라이언트 인스턴스 가져오기
    record_client = get_diagnosis_record_client()
    record_client.set_token(st.session_state.access_token)

    # 진단 기록 메타데이터 조회
    metadata_response = record_client.get_diagnosis_record_metadata(diagnosis_id)

    if not metadata_response.success or not metadata_response.data:
        st.error("진단 기록 메타데이터를 불러올 수 없습니다.")
        if metadata_response.error:
            st.error(metadata_response.error)
        return

    metadata = metadata_response.data

    # 메타데이터 표시
    st.write("### 진단 정보")

    st.markdown(
        """
    <style>
    [data-testid="stMetric"] > div {
        font-size: 24px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.expander("진단 정보", expanded=True):
        # 카드 형태로 메타데이터 표시
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("진단 유형", get_diagnosis_type_display(metadata.type))
            st.metric("평가 점수", f"{metadata.score:.2f}점")

        with col2:
            st.metric("레벨", metadata.level)
            st.metric("소요 시간", f"{metadata.time_spent:.2f}초")
        with col3:
            created_at = metadata.created_at
            st.metric("진단 일시", format_datetime(created_at))
            st.metric("FPS", f"{metadata.fps:.2f}")

    # 파일 다운로드 및 표시
    filename, df = record_client.download_diagnosis_file(diagnosis_id)

    if df is not None:
        st.write("### 진단 결과 시각화")
        report(df, filename, metadata.type, metadata.fps)
    else:
        st.error("진단 결과 파일을 불러올 수 없습니다.")


def render_diagnosis_record_list(patient_id: int, start_date: datetime, end_date: datetime):
    """환자의 진단 기록 목록을 표시하고 선택된 기록을 처리합니다."""
    if not patient_id:
        st.warning("환자를 선택해주세요.")
        return

    # 진단 기록 클라이언트 인스턴스 가져오기
    record_client = get_diagnosis_record_client()
    record_client.set_token(st.session_state.access_token)

    # 진단 기록 목록 조회
    response = record_client.get_patient_diagnosis_records(patient_id, start_date, end_date)

    if not response.success or not response.data:
        st.info("조회된 진단 기록이 없습니다.")
        if response.error:
            st.error(f"오류: {response.error}")
        return

    records = response.data

    # 기록 목록 표시 및 선택 컴포넌트
    st.write("### 진단 데이터 목록")

    # 데이터 가공
    options = []
    id_map = {}

    for record in records:
        display_text = f"{format_datetime(record.created_at)} - {get_diagnosis_type_display(record.type)} (레벨 {record.level})"
        options.append(display_text)
        id_map[display_text] = record.id

    # 선택 컴포넌트
    selected_option = st.selectbox("진단 선택", options=options)

    if selected_option:
        selected_id = id_map[selected_option]
        # 선택된 기록의 상세 정보 표시
        render_diagnosis_record_detail(selected_id)


def main_page():
    st.write("# 데이터베이스")

    # 현재 선택된 환자 ID 가져오기
    patient = st.session_state.get("selected_patient", None)
    if patient is None:
        st.warning("환자를 선택하거나 환자 관리 페이지에서 신규 환자를 등록해주세요.")
        return

    patient_id = patient.id

    # 날짜 선택 컴포넌트
    start_date, end_date = date_selector()

    # 환자의 진단 기록 목록 표시 및 선택
    if patient_id and start_date and end_date:
        render_diagnosis_record_list(patient_id, start_date, end_date)
    else:
        st.info("환자와 날짜를 선택하면 진단 기록이 표시됩니다.")


def side_bar():
    sidebar_navigation()
    with st.sidebar:
        st.image(WONJU_LOGO_URL, use_container_width=True)
        st.caption(DATABASE_DESCRIPTION)
        st.write("---")
        render_patient_dropdown_and_form()
        st.markdown("---")
        st.image(WHATSLAB_LOGO_URL, use_container_width=False, width=LOGO_WIDTH)


if __name__ == "__main__":
    st.set_page_config(page_title="데이터베이스", page_icon=YENSEI_ICON_URL, layout="wide")

    if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
        st.switch_page("main.py")

    local_css(MAIN_CSS_PATH)
    side_bar()
    main_page()
