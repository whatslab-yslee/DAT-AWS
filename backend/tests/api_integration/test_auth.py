from .utils import login_user, register_user


def test_register_doctor_success(client):
    response = register_user(client, "doctor1", "password123", "Dr. Kim", "DOCTOR")
    assert response.status_code == 201
    assert response.json()["login_id"] == "doctor1"
    assert response.json()["name"] == "Dr. Kim"
    assert response.json()["role"] == "DOCTOR"


def test_register_duplicate_login_id(client):
    register_user(client, "doctor2", "password123", "Dr. Lee", "DOCTOR")
    response = register_user(client, "doctor2", "password456", "Dr. Park", "DOCTOR")
    assert response.status_code == 400
    assert "이미 사용 중인 로그인 ID입니다" in response.json()["detail"]


def test_register_invalid_admin_code(client):
    response = register_user(client, "doctor3", "password123", "Dr. Choi", "DOCTOR", admin_code="wrong")
    assert response.status_code == 400
    assert "관리자 코드가 일치하지 않습니다" in response.json()["detail"]


def test_login_success(client):
    register_user(client, "doctor4", "password123", "Dr. Kang", "DOCTOR")
    response = login_user(client, "doctor4", "password123")
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_invalid_credentials(client):
    register_user(client, "doctor5", "password123", "Dr. Go", "DOCTOR")
    response = login_user(client, "doctor5", "wrongpassword")
    assert response.status_code == 401
    assert "로그인 ID 또는 비밀번호가 일치하지 않습니다" in response.json()["detail"]


def test_get_current_user_info(client):
    register_user(client, "doctor6", "password123", "Dr. Han", "DOCTOR")
    login_response = login_user(client, "doctor6", "password123")
    access_token = login_response.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["login_id"] == "doctor6"
    assert response.json()["name"] == "Dr. Han"
    assert response.json()["role"] == "DOCTOR"


def test_logout_and_refresh(client):
    register_user(client, "doctor11", "password123", "Dr. Kim", "DOCTOR")
    login_response = login_user(client, "doctor11", "password123")
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401
