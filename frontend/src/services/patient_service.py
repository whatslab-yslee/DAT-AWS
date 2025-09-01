from typing import Optional

from api_clients.patient_client import get_patient_client
from api_clients.schemas.patient_schema import PatientResponse
import pandas as pd
import streamlit as st


# 새 환자 추가 옵션 상수
NEW_PATIENT_OPTION = "== 새 환자 추가 =="


def render_patient_dropdown_and_form():
    """환자 드롭다운 UI와 환자 등록 폼을 렌더링합니다."""
    try:
        # 환자 목록 확인
        patients = st.session_state.get("patients", [])

        if not patients:
            st.warning("등록된 환자가 없습니다. 환자 관리 페이지에서 환자를 등록해주세요.")
            return

        # 환자 표시 형식 생성: "환자이름 (환자코드)"
        patient_display_options = [f"{patient.name} ({patient.code})" for patient in patients]

        # 드롭다운으로 환자 선택
        is_on_examination = st.session_state.get("on_examination", False)
        selected_option = st.selectbox(
            "환자 선택",
            patient_display_options,
            disabled=is_on_examination,
        )

        selected_option_index = patient_display_options.index(selected_option)
        st.session_state.selected_patient = patients[selected_option_index]

    except Exception as e:
        st.error("환자 목록을 처리하는 중 오류가 발생했습니다.")
        print(f"환자 목록 처리 오류: {str(e)}")
        return


def render_patient_registration_form():
    """환자 추가 폼을 렌더링합니다."""

    st.markdown("### 신규 환자 등록")

    with st.form("patient_registration_form", clear_on_submit=True):
        patient_name = st.text_input("환자 이름", key="new_patient_name")
        # patient_code = st.text_input("환자 코드 (선택사항)", key="new_patient_code")

        submitted = st.form_submit_button("등록")
        if submitted:
            _handle_registration_form_submit(patient_name=patient_name)


def _handle_registration_form_submit(patient_name: str, patient_code: Optional[str] = None):
    """환자 등록 폼 제출 처리"""
    if not patient_name:
        st.error("환자 이름을 입력해주세요.")
        return

    # 환자 생성 시도
    success, patient_id = create_patient(patient_name, patient_code)
    if success:
        # 등록 성공 시 환자 목록 새로고침
        refresh_patient_list()

        # 새로 등록된 환자를 현재 선택된 환자로 설정
        st.session_state.selected_patient = next((p for p in st.session_state.patients if p.id == patient_id), None)
        st.toast(f"환자 '{patient_name}'이(가) 등록되었습니다.")


def _render_patient_row(row):
    """환자 행을 렌더링합니다."""
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
    with col1:
        st.write(f"{row['이름']} ({row['코드']}) - {row['생성일']}")
    with col2:
        if st.button("수정", key=f"edit_{row['id']}"):
            st.session_state.editing_patient_id = row["id"]
            st.session_state.editing_patient_name = row["이름"]
            st.session_state.editing_patient_code = row["코드"]
            st.rerun()
    with col3:
        if st.button("삭제", key=f"delete_{row['id']}"):
            if delete_patient(row["id"]):
                st.success("환자가 삭제되었습니다.")
                refresh_patient_list()
                st.rerun()


def _render_edit_form():
    """환자 수정 폼을 렌더링합니다."""
    if not st.session_state.get("editing_patient_id"):
        return

    st.markdown("### 환자 정보 수정")
    with st.form("patient_edit_form"):
        edited_name = st.text_input("환자 이름", value=st.session_state.editing_patient_name)
        edited_code = st.text_input("환자 코드", value=st.session_state.editing_patient_code)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("저장"):
                if update_patient(st.session_state.editing_patient_id, edited_name, edited_code):
                    st.success("환자 정보가 수정되었습니다.")
                    refresh_patient_list()
                    st.session_state.editing_patient_id = None
                    st.rerun()
        with col2:
            if st.form_submit_button("취소"):
                st.session_state.editing_patient_id = None
                st.rerun()


def render_patients_table():
    """환자 목록을 테이블로 렌더링합니다."""
    st.markdown("### 환자 목록")

    patients: list[PatientResponse] = st.session_state.patients
    if not patients:
        st.warning("등록된 환자가 없습니다.")
        return

    search_query = st.text_input("환자 검색", placeholder="이름 또는 코드로 검색")
    filtered_patients = [
        p for p in patients if not search_query or search_query.lower() in p.name.lower() or (p.code and search_query.lower() in p.code.lower())
    ]

    if not filtered_patients:
        st.info("검색 결과가 없습니다.")
        return

    df = pd.DataFrame([(p.id, p.name, p.code, p.created_at.split("T")[0]) for p in filtered_patients], columns=["id", "이름", "코드", "생성일"])

    for _, row in df.iterrows():
        _render_patient_row(row)

    _render_edit_form()


def create_patient(name: str, code: Optional[str] = None) -> bool:
    """환자를 생성합니다.

    Args:
        name: 환자 이름
        code: 환자 코드 (선택적)

    Returns:
        bool: 생성 성공 여부
    """
    try:
        if not st.session_state.get("is_logged_in", False) or not st.session_state.get("access_token"):
            st.error("로그인이 필요합니다.")
            return False, -1

        patient_client = get_patient_client()
        patient_client.set_token(st.session_state.access_token)
        response = patient_client.create_patient(name=name, code=code)

        return response.success, response.data.id
    except Exception as e:
        st.error("환자 등록 중 오류가 발생했습니다.")
        st.error(str(e))
        return False, -1


def refresh_patient_list():
    """환자 목록을 새로고침합니다."""
    try:
        if not st.session_state.get("is_logged_in", False) or not st.session_state.get("access_token"):
            return False

        patient_client = get_patient_client(token=st.session_state.access_token)
        response = patient_client.get_patients()

        if response.success and response.data:
            st.session_state.patients = response.data
            return True
        else:
            st.session_state.patients = []
            if response.error:
                print(f"환자 목록 갱신 오류: {response.error}")
            else:
                print("환자 목록 갱신 실패: 응답 데이터 없음")
            return False
    except Exception as e:
        st.session_state.patients = []
        print(f"환자 목록 갱신 중 예외 발생: {str(e)}")
        return False


def update_patient(patient_id: int, name: str, code: Optional[str] = None) -> bool:
    """환자 정보를 수정합니다.

    Args:
        patient_id: 환자 ID
        name: 환자 이름
        code: 환자 코드 (선택적)

    Returns:
        bool: 수정 성공 여부
    """
    try:
        if not st.session_state.get("is_logged_in", False) or not st.session_state.get("access_token"):
            st.error("로그인이 필요합니다.")
            return False

        patient_client = get_patient_client()
        patient_client.set_token(st.session_state.access_token)
        response = patient_client.update_patient(patient_id=patient_id, name=name, code=code)

        return response.success
    except Exception as e:
        st.error("환자 정보 수정 중 오류가 발생했습니다.")
        st.error(str(e))
        return False


def delete_patient(patient_id: int) -> bool:
    """환자를 삭제합니다.

    Args:
        patient_id: 환자 ID

    Returns:
        bool: 삭제 성공 여부
    """
    try:
        if not st.session_state.get("is_logged_in", False) or not st.session_state.get("access_token"):
            st.error("로그인이 필요합니다.")
            return False

        patient_client = get_patient_client()
        patient_client.set_token(st.session_state.access_token)
        response = patient_client.delete_patient(patient_id=patient_id)

        return response.success
    except Exception as e:
        st.error("환자 삭제 중 오류가 발생했습니다.")
        st.error(str(e))
        return False
