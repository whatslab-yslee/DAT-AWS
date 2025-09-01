from .utils import create_patient, login_user, register_user


def test_diagnosis_start_and_live(client):
    register_user(client, "doctor12", "password123", "Dr. Kim", "DOCTOR")
    login_response = login_user(client, "doctor12", "password123")
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    patient_response = create_patient(client, "Patient G", token=access_token)
    patient_id = patient_response.json()["id"]
    response = client.post("/diagnosis/start", json={"patient_id": patient_id, "type": "VR_BALANCE_BALL", "level": 1}, headers=headers)
    assert response.status_code in (400, 403, 404, 422)
    response = client.get("/diagnosis/live", headers=headers)
    assert response.status_code in (404, 403)


def test_diagnosis_record_list(client):
    register_user(client, "doctor13", "password123", "Dr. Kim", "DOCTOR")
    login_response = login_user(client, "doctor13", "password123")
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    patient_response = create_patient(client, "Patient H", token=access_token)
    patient_id = patient_response.json()["id"]
    import datetime

    today = datetime.datetime.now().date()
    response = client.get(f"/diagnosis/record/list?patient_id={patient_id}&start_date={today}T00:00:00&end_date={today}T23:59:59", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_diagnosis_record_metadata_fail(client):
    register_user(client, "doctor14", "password123", "Dr. Kim", "DOCTOR")
    login_response = login_user(client, "doctor14", "password123")
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/diagnosis/record/9999/metadata", headers=headers)
    assert response.status_code in (404, 403)
