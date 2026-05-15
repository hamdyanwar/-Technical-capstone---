from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .. import main, database, models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

main.app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(main.app)

def test_create_device():
    response = client.post(
        "/devices/",
        json={"name": "Test Anesthesia", "type": "Anesthesia Machine", "location": "OR-1", "status": "Active"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Anesthesia"
    assert "id" in data

def test_add_telemetry_and_health():
    # first create device
    response = client.post(
        "/devices/",
        json={"name": "Health Test Device", "type": "Anesthesia Machine", "location": "OR-2", "status": "Active"},
    )
    device_id = response.json()["id"]

    # add normal telemetry
    telemetry_data = {
        "pressure": 35.0,
        "flow_rate": 50.0,
        "gas_level": 90.0,
        "battery_level": 100.0
    }
    response = client.post(f"/devices/{device_id}/telemetry", json=telemetry_data)
    assert response.status_code == 200

    # check health
    response = client.get(f"/devices/{device_id}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["status"] == "Good"
    assert data["analysis"]["health_score"] == 100

def test_health_warning():
    # create device
    response = client.post(
        "/devices/",
        json={"name": "Warning Device", "type": "Anesthesia Machine", "location": "OR-3", "status": "Active"},
    )
    device_id = response.json()["id"]

    # add bad telemetry (low pressure)
    telemetry_data = {
        "pressure": 20.0, # Below 30
        "flow_rate": 50.0,
        "gas_level": 90.0,
        "battery_level": 100.0
    }
    client.post(f"/devices/{device_id}/telemetry", json=telemetry_data)

    # check health
    response = client.get(f"/devices/{device_id}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["status"] != "Good"
    assert "Low Pressure" in data["analysis"]["issues"]
