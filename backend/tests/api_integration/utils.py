from fastapi.testclient import TestClient


def register_user(client: TestClient, login_id: str, password: str, name: str, role: str, admin_code: str = "1234"):
    response = client.post(
        "/auth/register",
        json={
            "login_id": login_id,
            "password": password,
            "name": name,
            "role": role,
            "admin_code": admin_code,
        },
    )
    return response


def login_user(client: TestClient, login_id: str, password: str):
    response = client.post(
        "/auth/login",
        json={"login_id": login_id, "password": password},
    )
    return response


def create_patient(client: TestClient, name: str, code: str = None, token: str = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    payload = {"name": name}
    if code:
        payload["code"] = code
    response = client.post("/patients", json=payload, headers=headers)
    return response


def get_patients(client: TestClient, token: str = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.get("/patients", headers=headers)
    return response


def update_patient(client: TestClient, patient_id: int, name: str, token: str = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.put(f"/patients/{patient_id}", json={"name": name}, headers=headers)
    return response


def delete_patient(client: TestClient, patient_id: int, token: str = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.delete(f"/patients/{patient_id}", headers=headers)
    return response
