from api_clients.auth_client import get_auth_client
from api_clients.patient_client import get_patient_client
from api_clients.schemas import TokenResponse
import streamlit as st
from utils import extract_expiry_from_token, get_datetime_from_timestamp, get_datetime_now


# TODO: Renderer / Handler 분리


def render_login_ui():
    st.markdown("### 로그인")

    with st.form("login_form", border=False):
        login_id = st.text_input("아이디", key="login_id")
        password = st.text_input("비밀번호", type="password", key="login_password")
        if st.form_submit_button("로그인"):
            handle_login(login_id, password, auth_client=get_auth_client())


def render_logout_ui():
    st.write(f"사용자: {st.session_state.userid}님")
    logout_button = st.button("로그아웃")
    if logout_button:
        handle_logout(auth_client=get_auth_client())


def handle_register(login_id, password, confirm_password, auth_client):
    if not login_id or not password:
        st.error("아이디와 비밀번호를 모두 입력해주세요.")
        return

    if password != confirm_password:
        st.error("비밀번호가 일치하지 않습니다.")
        return

    response = auth_client.register(login_id, password)

    if response.success:
        st.success("회원가입이 완료되었습니다. 로그인 탭에서 로그인해주세요.")
    else:
        # 오류 메시지 표시
        st.error(f"{response.error}")


def handle_login(login_id, password, auth_client=None):
    if not auth_client:
        auth_client = get_auth_client()

    if not login_id or not password:
        st.error("아이디와 비밀번호를 모두 입력해주세요.")
        return

    response = auth_client.login(login_id, password)

    if response.success and response.data:
        # 토큰 정보 저장
        token_data = response.data
        st.session_state.access_token = token_data.access_token

        # 토큰 만료 시간 처리
        expiry_timestamp = extract_expiry_from_token(token_data.access_token)
        st.session_state.token_expiry = get_datetime_from_timestamp(expiry_timestamp)

        # 사용자 정보 가져오기
        user_response = auth_client.get_user_info(st.session_state.access_token)
        if user_response.success and user_response.data:
            user_data = user_response.data
            st.session_state.userid = user_data.login_id
            st.session_state.is_logged_in = True

            # 환자 목록 가져오기
            load_patient_list()
            st.rerun()
        else:
            st.error("사용자 정보를 가져오는데 실패했습니다.")
    else:
        st.error(response.error)


def handle_logout(auth_client):
    if "access_token" in st.session_state:
        auth_client.logout(st.session_state.access_token)

    st.session_state.clear()
    st.rerun()


def try_auto_login(auth_client):
    try:
        response = auth_client.refresh_token()
        if not response.success:
            return False

        token_data = response.data
        update_token_info(token_data)

        login_success = update_user_info(auth_client, st.session_state.access_token)
        if login_success:
            # 환자 목록 가져오기
            load_patient_list()

        return login_success
    except Exception:
        return False


def refresh_expired_token(auth_client):
    try:
        response = auth_client.refresh_token()
        if not response.success:
            handle_logout(auth_client)
            return False

        token_data = response.data
        update_token_info(token_data)
        return True
    except Exception:
        handle_logout(auth_client)
        return False


def validate_access_token(auth_client):
    try:
        response = auth_client.get_user_info(st.session_state.access_token)
        if response.success:
            return True

        if refresh_expired_token(auth_client):
            return update_user_info(auth_client, st.session_state.access_token)

        return False
    except Exception:
        handle_logout(auth_client)
        return False


def update_token_info(token_data: TokenResponse):
    st.session_state.access_token = token_data.access_token

    # 토큰 만료 시간 처리
    expiry_timestamp = extract_expiry_from_token(token_data.access_token)
    st.session_state.token_expiry = get_datetime_from_timestamp(expiry_timestamp)


def update_user_info(auth_client, access_token):
    response = auth_client.get_user_info(access_token)
    if not response.success:
        return False

    user_data = response.data
    st.session_state.userid = user_data.login_id
    st.session_state.is_logged_in = True
    return True


def check_token_expiry(auth_client):
    if not st.session_state.is_logged_in:
        try_auto_login(auth_client)
        return

    try:
        # 토큰 만료 시간이 설정되어 있고, 현재 시간이 만료 시간 이후인 경우
        if "token_expiry" in st.session_state and st.session_state.token_expiry is not None and get_datetime_now() >= st.session_state.token_expiry:
            print("토큰이 만료되어 갱신을 시도합니다.")
            refresh_expired_token(auth_client)
        # 액세스 토큰이 있는 경우, 유효성 검증
        elif "access_token" in st.session_state and st.session_state.access_token is not None:
            validate_access_token(auth_client)
    except Exception as e:
        print(f"토큰 확인 중 오류 발생: {str(e)}")
        # 오류 발생 시 재로그인 유도
        if st.session_state.is_logged_in:
            st.warning("인증 정보가 만료되었습니다. 다시 로그인해주세요.")
            handle_logout(auth_client)


def load_patient_list():
    """환자 목록을 가져와 세션 상태에 저장합니다."""
    try:
        if not st.session_state.is_logged_in or not st.session_state.access_token:
            return False

        patient_client = get_patient_client()
        patient_client.set_token(st.session_state.access_token)
        response = patient_client.get_patients()

        if response.success and response.data:
            st.session_state.patients = response.data
            return True
        elif response.data is None:
            st.session_state.patients = []
            return True
        else:
            print(f"환자 목록 조회 오류: {response.error}")
            return False
    except Exception as e:
        print(f"환자 목록 조회 예외: {str(e)}")
        return False


def init_auth_states(auth_client):
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "userid" not in st.session_state:
        st.session_state.userid = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "token_expiry" not in st.session_state:
        st.session_state.token_expiry = None
    if "patients" not in st.session_state:
        st.session_state.patients = []

    # 이미 로그인 상태로 설정되어 있으면, 토큰 유효성 확인
    if st.session_state.is_logged_in and st.session_state.access_token is not None and st.session_state.userid is not None:
        check_token_expiry(auth_client=auth_client)

        # 환자 목록이 없는 경우 로드
        if not st.session_state.patients:
            load_patient_list()
    else:
        # 로그인 상태가 아니면 자동 로그인 시도
        try_auto_login(auth_client)
