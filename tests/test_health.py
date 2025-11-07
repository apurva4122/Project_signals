from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_ping():
    client = TestClient(create_app())
    response = client.get("/api/v1/health/ping")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"

