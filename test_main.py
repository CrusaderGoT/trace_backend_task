from fastapi.testclient import TestClient

from main import FarmerResponse, app

client = TestClient(app)

VALID_PAYLOAD = {
    "farmer_name": "John Doe",
    "farmer_id": "NG-1234567890",
    "latitude": 6.5244,
    "longitude": 3.3792,
    "farm_size_hectares": 10.5,
    "commodity": "cocoa",
    "agent_id": "AGENT-001",
    "submitted_at": "2026-05-26T15:02:23.641Z",
}

INVALID_PAYLOAD = {
    "farmer_id": "NG1234567890",
    "farmer_name": "",
    "latitude": 120,
    "longitude": -200,
    "farm_size_hectares": -5,
    "commodity": "",
    "agent_id": 12345,
    "submitted_at": "26-05-2026",
}


def test_successful_registration():
    response = client.post("/api/v1/farms/register", json=VALID_PAYLOAD)

    assert response.status_code == 201

    assert FarmerResponse.model_validate(response.json())  # Validate response structure

    assert response.json()["passport_status"] == "PENDING"


def test_duplicate_detection():
    # since the same client process is used, the DB retains all data for this entire test file run
    response = client.post("/api/v1/farms/register", json=VALID_PAYLOAD)

    assert response.status_code == 409


def test_invalid_gps_coord():
    # chnage coordinates to invalid numbers
    payload = VALID_PAYLOAD.copy()
    payload["latitude"] = 100
    payload["longitude"] = 200

    response = client.post("/api/v1/farms/register", json=payload)

    assert response.status_code == 422


def test_invalid_commodity():
    payload = VALID_PAYLOAD.copy()
    payload["commodity"] = "rice"

    response = client.post("/api/v1/farms/register", json=payload)

    assert response.status_code == 422


def test_missing_required_field():
    payload = VALID_PAYLOAD.copy()
    del payload["agent_id"]

    response = client.post("/api/v1/farms/register", json=payload)

    assert response.status_code == 422
