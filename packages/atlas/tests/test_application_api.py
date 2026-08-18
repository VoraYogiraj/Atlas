from fastapi.testclient import TestClient

from atlas.application.api import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Atlas",
        "status": "online",
        "version": "0.1.0",
    }


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}