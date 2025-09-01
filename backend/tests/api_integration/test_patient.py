from app.schemas.patient_schema import PatientResponse

from .utils import create_patient, delete_patient, get_patients, login_user, register_user, update_patient


def test_create_patient_success(client):
    register_user(client, "doctor7", "password123", "Dr. Park", "DOCTOR")
    login_response = login_user(client, "doctor7", "password123")
    access_token = login_response.json()["access_token"]
    response = create_patient(client, "Patient A", token=access_token)
    assert response.status_code == 201
    assert response.json()["name"] == "Patient A"
    assert "code" in response.json()


def test_create_patient_unauthorized(client):
    response = create_patient(client, "Patient B")
    assert response.status_code == 401


def test_get_doctor_patients_success(client):
    register_user(client, "doctor8", "password123", "Dr. Seo", "DOCTOR")
    login_response = login_user(client, "doctor8", "password123")
    access_token = login_response.json()["access_token"]
    create_patient(client, "Patient C", token=access_token)
    create_patient(client, "Patient D", token=access_token)
    response = get_patients(client, token=access_token)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Patient C" or response.json()[0]["name"] == "Patient D"


def test_update_patient_success(client):
    register_user(client, "doctor9", "password123", "Dr. Kim", "DOCTOR")
    login_response = login_user(client, "doctor9", "password123")
    access_token = login_response.json()["access_token"]
    create_patient_response = create_patient(client, "Patient E", token=access_token)
    patient_id = create_patient_response.json()["id"]
    response = update_patient(client, patient_id, "Patient E Updated", token=access_token)
    assert response.status_code == 200
    updated_patient_response = PatientResponse.model_validate(response.json())
    assert updated_patient_response.name == "Patient E Updated"


def test_delete_patient_success(client):
    register_user(client, "doctor10", "password123", "Dr. Lee", "DOCTOR")
    login_response = login_user(client, "doctor10", "password123")
    access_token = login_response.json()["access_token"]
    create_patient_response = create_patient(client, "Patient F", token=access_token)
    patient_id = create_patient_response.json()["id"]
    response = delete_patient(client, patient_id, token=access_token)
    assert response.status_code == 204
    response = get_patients(client, token=access_token)
    assert response.status_code == 200
    patients = response.json()
    assert all(patient["id"] != patient_id for patient in patients)
